from form import Form, FilingStatus
from f1040sse import F1040sse
from f1040sa import F1040sa
from f1040sd import F1040sd
from f2441 import F2441
from f6251 import F6251
from f8606 import F8606
from f8801 import F8801
#from f8801_2019 import F8801_2019
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
    STD_DED = [12000, 24000, 12000, 18000, 24000]
    BRACKET_RATES = [0.10, 0.12, 0.22, 0.24, 0.32, 0.35, 0.37]
    BRACKET_LIMITS = [
        [9525, 38700, 82500, 157500, 200000, 500000],   # SINGLE
        [19050, 77400, 165000, 315000, 400000, 600000], # JOINT
        [9525, 38700, 82500, 157500, 200000, 300000],   # SEPARATE
        [13600, 51800, 82500, 157500, 200000, 500000],  # HEAD
        [19050, 77400, 165000, 315000, 400000, 600000], # WIDOW
    ]
    CAPGAIN15_LIMITS = [38600, 77200, 38600, 51700, 77200]
    CAPGAIN20_LIMITS = [425800, 479000, 239500, 452400, 479000]
    SS_MAX = 7960.80

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
        f['2b'] = inputs.get('taxable_interest')
        f['3a'] = inputs.get('qualified_dividends')
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

        f['s12'] = f.spouseSum(inputs, 'business_income')

        sd = F1040sd(inputs)
        f.addForm(sd)
        if sd.mustFile():
            f['s13'] = sd['21'] or sd['16']
        else:
            f['s13'] = inputs.get('capital_gain_dist')

        f['s10'] = inputs.get('state_refund_taxable')
        f['s19'] = inputs.get('unemployment')
        f['s22'] = f.rowsum(['s10', 's11', 's12', 's13',
                            's14', 's15b', 's16b', 's17', 's18', 's19', 's20b',
                            's21'])

        f.comment['6'] = 'Total Income'
        f['6'] = f.rowsum(['1', '2b', '3b', '4b', '5b', 's22'])

        if inputs['status'] == FilingStatus.JOINT:
            if sse[0].mustFile() or sse[1].mustFile():
                f['s27'] = ((sse[0]['A6'] or sse[0]['B13'] or 0) +
                            (sse[1]['A6'] or sse[1]['B13'] or 0))
        else:
            if sse.mustFile():
                f['s27'] = sse['A6'] or sse['B13']
        f['s36'] = f.rowsum(['s23', 's24', 's25', 's26', 's27', 's28', 's29',
                            's30', 's31a', 's32', 's33', 's34', 's35'])

        f.comment['7'] = 'AGI'
        f['7'] = f['6'] - f['s36']

        sa = F1040sa(inputs, f)
        std = f.STD_DED[inputs['status']]
        if 'itemize_deductions' in inputs:
            sa.must_file = inputs['itemize_deductions']
        else:
            sa.must_file = sa['17'] > std

        f.addForm(sa)
        if sa.mustFile():
            f.comment['8'] = 'Itemized deductions'
            f['8'] = sa['17']
        else:
            # TODO: claimed as dependent or born before Jan 2, 1952 or blind
            f.comment['8'] = 'Standard deduction'
            f['8'] = std

        f.comment['10'] = 'Taxable Income'
        f['10'] = max(0, f['7'] - f['8'] - f['9'])

        # TODO: Schedule D tax worksheet
        assert(not sd['18'] and not sd['19'])

        f.comment['11a'] = 'Regular Tax'
        f['11a'] = f.div_cap_gain_tax_worksheet(inputs, sd)['27']

        # Compute line s48 now because it's needed by AMT
        foreign_tax = inputs.get('foreign_tax', 0)
        assert(foreign_tax < 300 or (foreign_tax < 600 and inputs['status'] == FilingStatus.JOINT))
        if foreign_tax:
            f['s48'] = foreign_tax

        f6251 = F6251(inputs, f, sa if sa.mustFile() else None, sd, sd)
        f.comment['s45'] = 'AMT'
        f['s45'] = f6251.get('11')
        f.addForm(f6251)

        f['s47'] = f.rowsum(['s45', 's46'])

        f.comment['11'] = 'Tax'
        f['11'] = f['11a'] + f['s47']

        f['s49'] = f2441.part2(f)

        f.comment['12a'] = 'Child Tax Credit'
        f['12a'] = f.child_tax_credit(inputs)

        f8801 = F8801(inputs, f, f6251)
        f['s54'] = f8801.get('25')
        f.addForm(f8801)

        f.comment['s55'] = 'Nonrefundable credits'
        f['s55'] = f.rowsum(['s48', 's49', 's50', 's51', 's52', 's53', 's54'])

        f.comment['12'] = 'Total Credits'
        f['12'] = f['12a'] + f['s55']

        f['13'] = max(0, f['11'] - f['12'])

        if inputs['status'] == FilingStatus.JOINT:
            if sse[0].mustFile() or sse[1].mustFile():
                f['s57'] = ((sse[0]['A5'] or sse[0]['B12'] or 0) +
                            (sse[1]['A5'] or sse[1]['B12'] or 0))
        else:
            if sse.mustFile():
                f['s57'] = sse['A5'] or sse['B12']
        f8959 = F8959(inputs, sse)
        f8960 = F8960(inputs, f, sa if sa.mustFile() else None)
        f['s62'] = f8959['18'] + f8960['17'] or None
        f.addForm(f8959)
        f.addForm(f8960)
        f['s64'] = f.rowsum(['s57', 's58', 's59', 's60a', 's60b', 's61', 's62'])

        f.comment['14'] = 'Other Taxes'
        f['14'] = f['s64']
        f.comment['15'] = 'Total Tax'
        f['15'] = f.rowsum(['13', '14'])

        f.comment['16'] = 'Withholding'
        f['16'] = inputs.get('withholding', 0) + f8959['24']

        f['s66'] = inputs.get('estimated_payments')

        if inputs.get('ss_withheld'):
            if inputs['status'] == FilingStatus.JOINT:
                if inputs['ss_withheld'][0] > f.SS_MAX:
                    f['s72'] = inputs['ss_withheld'][0] - f.SS_MAX
                if inputs['ss_withheld'][1] > f.SS_MAX:
                    f['s72'] += inputs['ss_withheld'][1] - f.SS_MAX
            else:
                if inputs['ss_withheld'] > f.SS_MAX:
                    f['s72'] = inputs['ss_withheld'] - f.SS_MAX

        f['s75'] = f.rowsum(['s66', 's70', 's71', 's72', 's73', 's74'])

        # TODO: EIC
        f.comment['17'] = 'Refundable Credits'
        f['17'] = f['s75']

        f.comment['18'] = 'Total payments'
        f['18'] = f.rowsum(['16', '17'])
        if f['18'] > f['15']:
            f.comment['19'] = 'Refund'
            f['19'] = f['18'] - f['15']
        else:
            f.comment['22'] = 'Amount you owe'
            f['22'] = f['15'] - f['18']

        #f8801_2019 = F8801_2019(inputs, f, f6251, f8801, sd)
        #f.addForm(f8801_2019)

    def div_cap_gain_tax_worksheet(f, inputs, sched_d):
        w = {}
        w['1'] = f['10']
        w['2'] = f['3a']
        if sched_d.mustFile():
            w['3'] = max(0, min(sched_d['15'], sched_d['16']))
        else:
            w['3'] = f['s13']
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
        w['4'] = f['7']
        if inputs['status'] == FilingStatus.JOINT:
            w['5'] = 400000
        else:
            w['5'] = 200000
        w['6'] = math.ceil(max(0, w['4'] - w['5']) / 1000.0) * 1000
        w['7'] = w['6'] * .05
        if w['3'] <= w['7']:
            return 0
        w['8'] = w['3'] - w['7']
        w['9'] = f['11']
        # TODO: forms 5696, 8910, 8936, schedule R
        w['10'] = f.rowsum(['s48', 's49', 's50', 's51']) or 0
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
