from form import Form, FilingStatus
from f1040sse import F1040sse
from f1040sa import F1040sa
from f1040sd import F1040sd
from f2441 import F2441
from f6251 import F6251
from f8606 import F8606
from f8801 import F8801
from f8801_2018 import F8801_2018
from f8959 import F8959
from f8960 import F8960
import copy
import math

# Inputs:
#   status (required)     - One of FilingStatus
#   exemptions (required) - A number
#   wages (optional)      - in dollars
#   wages_ss (optional)   - social security portion of wages
#   taxable_interest (optional)
#   tax_exempt_interest (optional)

class F1040(Form):
    STD_DED = [6350, 12700, 6350, 9350, 12700]
    EXEMPTION = 4050
    BRACKET_RATES = [0.10, 0.15, 0.25, 0.28, 0.33, 0.35, 0.396]
    BRACKET_LIMITS = [
        [9325, 37950, 91900, 191650, 416700, 418400],   # SINGLE
        [18650, 75900, 153100, 233350, 416700, 470700], # JOINT
        [9375, 37950, 76550, 116675, 208350, 235350],   # SEPARATE
        [13350, 50800, 131200, 212500, 416700, 444550], # HEAD
        [18650, 75900, 153100, 233350, 416700, 470700], # WIDOW
    ]
    SS_MAX = 7886

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

        f['6d'] = inputs['exemptions']
        f['7'] = f.spouseSum(inputs, 'wages') + f2441['26']
        f['8a'] = inputs.get('taxable_interest')
        f['8b'] = inputs.get('tax_exempt_interest')
        f['9a'] = inputs.get('dividends')
        f['9b'] = inputs.get('qualified_dividends')
        f['12'] = f.spouseSum(inputs, 'business_income')

        sd = F1040sd(inputs)
        f.addForm(sd)
        if sd.mustFile():
            f['13'] = sd['21'] or sd['16']
        else:
            f['13'] = inputs.get('capital_gain_dist')

        if 'F8606' in inputs:
            if inputs['status'] == FilingStatus.JOINT:
                f8606 = [f.addForm(F8606(inputs, 0)),
                         f.addForm(F8606(inputs, 1))]
                f['15b'] = (f8606[0]['15c'] + f8606[0]['18'] + f8606[0]['25'] +
                            f8606[1]['15c'] + f8606[1]['18'] + f8606[1]['25']) \
                            or None
            else:
                f8606 = f.addForm(F8606(inputs, None))
                f['15b'] = f8606.rowsum(['15c', '18', '25'])

        f['19'] = inputs.get('unemployment')
        f['22'] = f.rowsum(['7', '8a', '9a', '10', '11', '12', '13',
                            '14', '15b', '16b', '17', '18', '19', '20b',
                            '21'])

        if inputs['status'] == FilingStatus.JOINT:
            if sse[0].mustFile() or sse[1].mustFile():
                f['27'] = ((sse[0]['A6'] or sse[0]['B13'] or 0) +
                           (sse[1]['A6'] or sse[1]['B13'] or 0))
        else:
            if sse.mustFile():
                f['27'] = sse['A6'] or sse['B13']
        f['36'] = f.rowsum(['23', '24', '25', '26', '27', '28', '29',
                            '30', '31a', '32', '33', '34', '35'])
        f.comment['37'] = 'AGI'
        f['37'] = f['22'] - f['36']
        f['38'] = f['37']

        sa = F1040sa(inputs, f)
        std = f.STD_DED[inputs['status']]
        if 'itemize_deductions' in inputs:
            file_sched_a = inputs['itemize_deductions']
        else:
            file_sched_a = sa['29'] > std

        if file_sched_a:
            f.comment['40'] = 'Itemized deductions'
            f['40'] = sa['29']
            f.addForm(sa)
        else:
            # TODO: claimed as dependent or born before Jan 2, 1952 or blind
            f.comment['40'] = 'Standard deduction'
            f['40'] = std

        f['41'] = f['38'] - f['40']
        f.comment['42'] = 'Exemptions'
        f['42'] = f.deduction_for_exemptions(inputs['status'])
        f.comment['43'] = 'Taxable income'
        f['43'] = max(0, f['41'] - f['42'])

        # TODO: Schedule D tax worksheet
        assert(not sd['18'] and not sd['19'])

        f.comment['44'] = 'Tax'
        f['44'] = f.div_cap_gain_tax_worksheet(inputs, sd)['27']

        # Compute line 46 and 48 now because it's needed by AMT
        foreign_tax = inputs.get('foreign_tax', 0)
        assert(foreign_tax < 300 or (foreign_tax < 600 and inputs['status'] == FilingStatus.JOINT))
        if foreign_tax:
            f['48'] = min(foreign_tax, f['44'] + f['46'])

        f6251 = F6251(inputs, f, sa if file_sched_a else None, sd)
        f.comment['45'] = 'AMT'
        f['45'] = f6251.get('35')
        f.addForm(f6251)

        f['47'] = f.rowsum(['44', '45', '46'])

        f['49'] = f2441.part2(f)

        f['52'] = f.child_tax_credit(inputs)
        f8801 = F8801(inputs, f, f6251)
        f['54'] = f8801.get('25')
        f.addForm(f8801)
        f.comment['55'] = 'Total credits'
        f['55'] = f.rowsum(['48', '49', '50', '51', '52', '53', '54'])
        f['56'] = max(0, f['47'] - f['55'])
        if inputs['status'] == FilingStatus.JOINT:
            if sse[0].mustFile() or sse[1].mustFile():
                f['57'] = ((sse[0]['A5'] or sse[0]['B12'] or 0) +
                           (sse[1]['A5'] or sse[1]['B12'] or 0))
        else:
            if sse.mustFile():
                f['57'] = sse['A5'] or sse['B12']
        f8959 = F8959(inputs, f, sse)
        f8960 = F8960(inputs, f, sa if file_sched_a else None)
        f['62'] = f8959['18'] + f8960['17'] or None
        f.addForm(f8959)
        f.addForm(f8960)
        f.comment['63'] = 'Total tax'
        f['63'] = f.rowsum(['56', '57', '58', '59', '60a', '60b', '61', '62'])
        f['64'] = inputs.get('withholding', 0) + f8959['24']
        f['65'] = inputs.get('estimated_payments')
        # TODO: EIC

        if inputs.get('ss_withheld'):
            if inputs['status'] == FilingStatus.JOINT:
                if inputs['ss_withheld'][0] > f.SS_MAX:
                    f['71'] = inputs['ss_withheld'][0] - f.SS_MAX
                if inputs['ss_withheld'][1] > f.SS_MAX:
                    f['71'] += inputs['ss_withheld'][1] - f.SS_MAX
            else:
                if inputs['ss_withheld'] > f.SS_MAX:
                    f['71'] = inputs['ss_withheld'] - f.SS_MAX

        f.comment['74'] = 'Total payments'
        f['74'] = f.rowsum(['64', '65', '66a', '67', '68', '69', '70', '71',
                            '72', '73'])
        if f['74'] > f['63']:
            f.comment['75'] = 'Refund'
            f['75'] = f['74'] - f['63']
        else:
            f.comment['78'] = 'Amount you owe'
            f['78'] = f['63'] - f['74']

        f8801_2018 = F8801_2018(inputs, f, f6251, f8801, sd)
        f.addForm(f8801_2018)

    def div_cap_gain_tax_worksheet(f, inputs, sched_d):
        w = {}
        w['1'] = f['43']
        w['2'] = f['9b']
        if sched_d.mustFile():
            w['3'] = max(0, min(sched_d['15'], sched_d['16']))
        else:
            w['3'] = f['13']
        w['4'] = w['2'] + w['3']
        w['5'] = 0 # TODO: form 4952
        w['6'] = max(0, w['4'] - w['5'])
        w['7'] = max(0, w['1'] - w['6'])
        w['8'] = f.BRACKET_LIMITS[inputs['status']][1]
        w['9'] = min(w['1'], w['8'])
        w['10'] = min(w['7'], w['9'])
        w['11'] = w['9'] - w['10']
        w['12'] = min(w['1'], w['6'])
        w['13'] = w['11']
        w['14'] = w['12'] - w['13']
        w['15'] = f.BRACKET_LIMITS[inputs['status']][5]
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

    def deduction_for_exemptions(f, status):
        w = {}
        w['2'] = f.EXEMPTION * f['6d']
        w['3'] = f['38']
        w['4'] = F1040sa.LIMITS[status]
        if w['3'] <= w['4']:
            return w['2']
        w['5'] = w['3'] - w['4']
        divisor = 1250.0 if status == FilingStatus.SEPARATE else 2500.0
        w['6'] = math.ceil(w['5'] / divisor)
        w['7'] = w['6'] * .02
        if w['7'] >= 1.0:
            return 0
        w['8'] = w['2'] * w['7']
        w['9'] = w['2'] - w['8']
        return w['9']

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
            return None
        w = {}
        w['1'] = inputs['qualifying_children'] * 1000
        w['2'] = f['38']
        if inputs['status'] == FilingStatus.JOINT:
            w['3'] = 110000
        elif inputs['status'] == FilingStatus.SEPARATE:
            w['3'] = 55000
        else:
            w['3'] = 75000
        w['4'] = math.ceil(max(0, w['2'] - w['3']) / 1000.0) * 1000
        w['5'] = w['4'] * .05
        if w['1'] <= w['5']:
            return None
        w['6'] = w['1'] - w['5']
        w['7'] = f['47']
        # TODO: forms 5696, 8910, 8936, schedule R
        w['8'] = f.rowsum(['48', '49', '50', '51'])
        if w['7'] == w['8']:
            raise RuntimeError('TODO: additional child tax credit')
            return None
        w['9'] = w['7'] - w['8']
        if w['6'] > w['9']:
            raise RuntimeError('TODO: additional child tax credit')
            w['10'] = w['9']
        else:
            w['10'] = w['6']
        return w['10']

    def title(f):
        return 'Form 1040'
