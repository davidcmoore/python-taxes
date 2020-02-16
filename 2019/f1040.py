from form import Form, FilingStatus
from f1040sse import F1040sse
from f1040sa import F1040sa
from f1040sd import F1040sd
from f2441 import F2441
from f6251 import F6251
from f8606 import F8606
from f8801 import F8801
#from f8801_2020 import F8801_2020
from f8959 import F8959
from f8960 import F8960
import copy
import math
import pprint

# Inputs:
#   status (required)     - One of FilingStatus
#   exemptions (required) - A number
#   wages (optional)      - in dollars
#   wages_ss (optional)   - social security portion of wages
#   taxable_interest (optional)
#   tax_exempt_interest (optional)

class F1040(Form):
    STD_DED = [12200, 24400, 12200, 18350, 24400]
    BRACKET_RATES = [0.10, 0.12, 0.22, 0.24, 0.32, 0.35, 0.37]
    BRACKET_LIMITS = [
        [9700, 39475, 84200, 160725, 204100, 510300],   # SINGLE
        [19400, 78950, 168400, 321450, 408200, 612350], # JOINT
        [9700, 39475, 84200, 160725, 204100, 306175],   # SEPARATE
        [13850, 52850, 84200, 160700, 204100, 510300],  # HEAD
        [19400, 78950, 168400, 321450, 408200, 612350], # WIDOW
    ]
    CAPGAIN15_LIMITS = [39375, 78750, 39375, 52750, 78750]
    CAPGAIN20_LIMITS = [434550, 488850, 244425, 461700, 488850]
    SS_MAX = 8239.80

    def __init__(f, inputs={}):
        super(F1040, f).__init__(inputs)

        f.must_file = True
        f.addForm(f)
        if inputs['status'] == FilingStatus.JOINT:
            sse = []
            for i in [0,1]:
                inputs2 = copy.copy(inputs)
                for j in ['wages', 'wages_ss', 'business_income']:
                    if j in inputs:
                        inputs2[j] = inputs[j][i]
                x = F1040sse(inputs2)
                f.addForm(x)
                sse.append(x)
        else:
            sse = F1040sse(inputs)
            f.addForm(sse)

        f2441 = F2441(inputs, sse)
        f.addForm(f2441)

        f.comment['1'] = 'Wages'
        f['1'] = f.spouseSum(inputs, 'wages') + f2441['26']
        f['2a'] = inputs.get('tax_exempt_interest')
        f.comment['2b'] = 'Taxable Interest'
        f['2b'] = inputs.get('taxable_interest')
        f['3a'] = inputs.get('qualified_dividends')
        f.comment['3b'] = 'Dividends'
        f['3b'] = inputs.get('dividends')

        if 'F8606' in inputs:
            if inputs['status'] == FilingStatus.JOINT:
                f8606 = [f.addForm(F8606(inputs, 0)),
                         f.addForm(F8606(inputs, 1))]
                f['4b'] = (f8606[0]['15c'] + f8606[0]['18'] + f8606[0]['25c'] +
                           f8606[1]['15c'] + f8606[1]['18'] + f8606[1]['25c']) \
                           or None
            else:
                f8606 = f.addForm(F8606(inputs, None))
                f['4b'] = f8606.rowsum(['15c', '18', '25c'])

        f.comment['6'] = 'Capital Gains'
        sd = F1040sd(inputs)
        f.addForm(sd)
        if sd.mustFile():
            f['6'] = sd['21'] or sd['16']
        else:
            f['6'] = inputs.get('capital_gain_dist')

        f['s1_1'] = inputs.get('state_refund_taxable')
        f['s1_3'] = f.spouseSum(inputs, 'business_income')
        f['s1_7'] = inputs.get('unemployment')

        f['s1_9'] = f.rowsum(['s1_1', 's1_2a', 's1_3', 's1_4',
                              's1_5', 's1_6', 's1_7', 's1_8'])
        f['7a'] = f.get('s1_9')

        f.comment['7b'] = 'Total Income'
        f['7b'] = f.rowsum(['1', '2b', '3b', '4b', '4d', '5b', '6', '7a'])

        if inputs['status'] == FilingStatus.JOINT:
            if sse[0].mustFile() or sse[1].mustFile():
                f['s1_14'] = ((sse[0]['A6'] or sse[0]['B13'] or 0) +
                              (sse[1]['A6'] or sse[1]['B13'] or 0))
        else:
            if sse.mustFile():
                f['s1_14'] = sse['A6'] or sse['B13']

        f['s1_22'] = f.rowsum(['s1_10', 's1_11', 's1_12', 's1_13', 's1_14',
                               's1_15', 's1_16', 's1_17', 's1_18a', 's1_19',
                               's1_20', 's1_21'])
        f['8a'] = f.get('s1_22')

        f.comment['8b'] = 'AGI'
        f['8b'] = f['7b'] - f['8a']

        sa = F1040sa(inputs, f)
        std = f.STD_DED[inputs['status']]
        if 'itemize_deductions' in inputs:
            sa.must_file = inputs['itemize_deductions']
        else:
            sa.must_file = sa['17'] > std

        f.addForm(sa)
        if sa.mustFile():
            f.comment['9'] = 'Itemized deductions'
            f['9'] = sa['17']
        else:
            # TODO: claimed as dependent or born before Jan 2, 1955 or blind
            f.comment['9'] = 'Standard deduction'
            f['9'] = std

        # TODO: Qualified Business Income Deduction, form 8995
        f['11a'] = f['9'] + f['10']

        f.comment['11b'] = 'Taxable Income'
        f['11b'] = max(0, f['8b'] - f['11a'])

        # TODO: Schedule D tax worksheet
        assert(not sd['18'] and not sd['19'])

        f.comment['12a'] = 'Regular Tax'
        f['12a'] = f.div_cap_gain_tax_worksheet(inputs, sd)['27']

        # Compute line s3_1 now because it's needed by AMT
        f.comment['s3_1'] = 'Foreign Tax Paid'
        foreign_tax = inputs.get('foreign_tax', 0)
        assert(foreign_tax < 300 or (foreign_tax < 600 and inputs['status'] == FilingStatus.JOINT))
        if foreign_tax:
            f['s3_1'] = foreign_tax

        f6251 = F6251(inputs, f, sa if sa.mustFile() else None, sd, sd)
        f.comment['s2_1'] = 'AMT'
        f['s2_1'] = f6251.get('11')
        f.addForm(f6251)

        f['s2_3'] = f.rowsum(['s2_1', 's2_2'])

        f.comment['12b'] = 'Tax'
        f['12b'] = f['12a'] + f['s2_3']

        f.comment['13a'] = 'Child Tax Credit'
        f['13a'] = f.child_tax_credit(inputs)

        f.comment['s3_2'] = 'Credit for child care expenses'
        f['s3_2'] = f2441.part2(f)

        f8801 = F8801(inputs, f, f6251)
        f['s3_6'] = f8801.get('25')
        f.addForm(f8801)

        f.comment['s3_7'] = 'Nonrefundable credits'
        f['s3_7'] = f.rowsum(['s3_1', 's3_2', 's3_3', 's3_4', 's3_5', 's3_6'])

        f.comment['13b'] = 'Total Credits'
        f['13b'] = f['13a'] + f['s3_7']

        f['14'] = max(0, f['12b'] - f['13b'])

        if inputs['status'] == FilingStatus.JOINT:
            if sse[0].mustFile() or sse[1].mustFile():
                f['s2_4'] = ((sse[0]['A5'] or sse[0]['B12'] or 0) +
                             (sse[1]['A5'] or sse[1]['B12'] or 0))
        else:
            if sse.mustFile():
                f['s2_4'] = sse['A5'] or sse['B12']

        f.comment['s2_8'] = 'NIIT and Additional Medicare Tax'
        f8959 = F8959(inputs, sse)
        f8960 = F8960(inputs, f, sa if sa.mustFile() else None)
        f['s2_8'] = f8959['18'] + f8960['17'] or None
        f.addForm(f8959)
        f.addForm(f8960)
        f['s2_10'] = f.rowsum(['s2_4', 's2_5', 's2_6', 's2_7a', 's2_7b',
                               's2_8'])

        f.comment['15'] = 'Other Taxes'
        f['15'] = f['s2_10']

        f.comment['16'] = 'Total Tax'
        f['16'] = f.rowsum(['14', '15'])

        f.comment['17'] = 'Withholding'
        f['17'] = inputs.get('withholding', 0) + f8959['24']

        f['s3_8'] = inputs.get('estimated_payments')

        # TODO: EIC, Additional Child Tax Credit

        if inputs.get('ss_withheld'):
            if inputs['status'] == FilingStatus.JOINT:
                if inputs['ss_withheld'][0] > f.SS_MAX:
                    f['s3_11'] = inputs['ss_withheld'][0] - f.SS_MAX
                if inputs['ss_withheld'][1] > f.SS_MAX:
                    f['s3_11'] += inputs['ss_withheld'][1] - f.SS_MAX
            else:
                if inputs['ss_withheld'] > f.SS_MAX:
                    f['s3_11'] = inputs['ss_withheld'] - f.SS_MAX

        f['s3_14'] = f.rowsum(['s3_8', 's3_9', 's3_10', 's3_11', 's3_12',
                               's3_13'])
        f['18d'] = f['s3_14']

        f.comment['18e'] = 'Refundable Credits'
        f['18e'] = f.rowsum(['18a', '18b', '18c', '18d'])

        f.comment['19'] = 'Total payments'
        f['19'] = f.rowsum(['17', '18e'])
        if f['19'] > f['16']:
            f.comment['20'] = 'Refund'
            f['20'] = f['19'] - f['16']
        else:
            f.comment['23'] = 'Amount you owe'
            f['23'] = f['16'] - f['19']

        #f8801_2020 = F8801_2020(inputs, f, f6251, f8801, sd)
        #f.addForm(f8801_2020)

    def div_cap_gain_tax_worksheet(f, inputs, sched_d):
        w = {}
        w['1'] = f['11b']
        w['2'] = f['3a']
        if sched_d.mustFile():
            w['3'] = max(0, min(sched_d['15'], sched_d['16']))
        else:
            w['3'] = f['6']
        w['4'] = w['2'] + w['3']
        w['5'] = 0 # TODO: form 4952
        w['6'] = max(0, w['4'] - w['5'])
        w['7'] = max(0, w['1'] - w['6'])
        w['8'] = f.CAPGAIN15_LIMITS[inputs['status']]
        w['9'] = min(w['1'], w['8'])
        w['10'] = min(w['7'], w['9'])
        w['11'] = w['9'] - w['10']
        w['12'] = min(w['1'], w['6'])
        w['13'] = w['11']
        w['14'] = w['12'] - w['13']
        w['15'] = f.CAPGAIN20_LIMITS[inputs['status']]
        w['16'] = min(w['1'], w['15'])
        w['17'] = w['7'] + w['11']
        w['18'] = max(0, w['16'] - w['17'])
        w['19'] = min(w['14'], w['18'])
        w['20'] = w['19'] * .15
        w['21'] = w['11'] + w['19']
        w['22'] = w['12'] - w['21']
        w['23'] = w['22'] * .20
        w['24'] = f.tax_worksheet(inputs['status'], w['7'])
        w['25'] = w['20'] + w['23'] + w['24']
        w['26'] = f.tax_worksheet(inputs['status'], w['1'])
        w['27'] = min(w['25'], w['26'])
        return w

    def tax_worksheet(f, status, val):
        # TODO: rounding of amounts less than 100000 to match tax table
        tax = 0
        prev = 0
        i = 0
        for lim in f.BRACKET_LIMITS[status]:
            if val <= lim:
                break
            tax += f.BRACKET_RATES[i] * (lim - prev)
            prev = lim
            i += 1
        tax += f.BRACKET_RATES[i] * (val - prev)
        return tax

    def child_tax_credit(f, inputs):
        if not inputs.get('qualifying_children'):
            return 0
        w = {}
        w['1'] = inputs['qualifying_children'] * 2000
        w['2'] = 0 # TODO: other dependents
        w['3'] = w['1'] + w['2']
        w['4'] = f['8b']
        if inputs['status'] == FilingStatus.JOINT:
            w['5'] = 400000
        else:
            w['5'] = 200000
        w['6'] = math.ceil(max(0, w['4'] - w['5']) / 1000.0) * 1000
        w['7'] = w['6'] * .05
        if w['3'] <= w['7']:
            return 0
        w['8'] = w['3'] - w['7']
        w['9'] = f['12b']
        # TODO: forms 5696, 8910, 8936, schedule R
        w['10'] = f.rowsum(['s3_1' 's3_2', 's3_3', 's3_4']) or 0
        if w['9'] == w['10']:
            raise RuntimeError('TODO: additional child tax credit')
            return None
        w['11'] = w['9'] - w['10']
        if w['8'] > w['11']:
            raise RuntimeError('TODO: additional child tax credit')
            w['12'] = w['11']
        else:
            w['12'] = w['8']
        return w['12']

    def title(f):
        return 'Form 1040'
