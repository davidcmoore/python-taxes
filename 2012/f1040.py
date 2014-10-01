
from form import Form, FilingStatus
from f1040sse import F1040sse
from f1040sa import F1040sa
from f1040sd import F1040sd
from f6251 import F6251
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
    STD_DED = [5950, 11900, 5950, 8700, 11900]
    EXEMPTION = 3800
    BRACKET_RATES = [0.10, 0.15, 0.25, 0.28, 0.33, 0.35]
    BRACKET_LIMITS = [
        [8700, 35350, 85650, 178650, 388350],   # SINGLE
        [17400, 70700, 142700, 217450, 388350], # JOINT
        [8700, 35350, 71350, 108725, 194175],   # SEPARATE
        [12400, 47350, 122300, 198050, 388350], # HEAD
        [17400, 70700, 142700, 217450, 388350], # WIDOW
    ]
    SS_MAX = 4624.20


    def __init__(f, inputs={}):
        super(F1040, f).__init__(inputs)

        f.must_file = True
        f.addForm(f)
        if inputs['status'] == FilingStatus.JOINT:
            sse = []
            for i in [0,1]:
                inputs2 = copy.copy(inputs)
                for j in ['wages', 'wages_ss', 'business_income']:
                    inputs2[j] = inputs[j][i]
                x = F1040sse(inputs2)
                f.addForm(x)
                sse.append(x)
        else:
            sse = F1040sse(inputs)
            f.addForm(sse)

        f['6d'] = inputs['exemptions']
        f['7'] = f.spouseSum(inputs, 'wages')
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
        f['37'] = f['22'] - f['36']
        f['38'] = f['37']

        sa = F1040sa(inputs, f)
        std = f.STD_DED[inputs['status']]
        file_sched_a = sa['29'] > std
        if file_sched_a:
            f['40'] = sa['29']
            f.addForm(sa)
        else:
            f['40'] = std

        f['41'] = f['38'] - f['40']
        f['42'] = f.EXEMPTION * f['6d']
        f['43'] = 0 if f['42'] > f['41'] else f['41'] - f['42']

        # TODO: Schedule D tax worksheet
        assert(not sd['18'] and not sd['19'])

        f['44'] = f.div_cap_gain_tax_worksheet(inputs, sd)

        # Compute line 47 now because it's needed by AMT
        foreign_tax = inputs.get('foreign_tax', 0)
        assert(foreign_tax < 300 or (foreign_tax < 600 and inputs['status'] == FilingStatus.JOINT))
        if foreign_tax:
            f['47'] = min(foreign_tax, f['44'])

        f6251 = F6251(inputs, f, sa if file_sched_a else None, sd)
        f['45'] = f6251.get('35')
        f.addForm(f6251)

        f['46'] = f.rowsum(['44', '45'])

        f['51'] = f.child_tax_credit(inputs)
        f['54'] = f.rowsum(['47', '48', '49', '50', '51', '52', '53'])
        f['55'] = max(0, f['46'] - f['54'])
        if inputs['status'] == FilingStatus.JOINT:
            if sse[0].mustFile() or sse[1].mustFile():
                f['56'] = ((sse[0]['A5'] or sse[0]['B12'] or 0) +
                           (sse[1]['A5'] or sse[1]['B12'] or 0))
        else:
            if sse.mustFile():
                f['56'] = sse['A5'] or sse['B12']
        f['61'] = f.rowsum(['55', '56', '57', '58', '59', '60'])
        f['62'] = inputs.get('withholding')
        f['63'] = inputs.get('estimated_payments')
        # TODO: EIC

        if inputs.get('ss_withheld'):
            if inputs['status'] == FilingStatus.JOINT:
                if inputs['ss_withheld'][0] > f.SS_MAX:
                    f['69'] = inputs['ss_withheld'][0] - f.SS_MAX
                if inputs['ss_withheld'][1] > f.SS_MAX:
                    f['69'] += inputs['ss_withheld'][1] - f.SS_MAX
            else:
                if inputs['ss_withheld'] > f.SS_MAX:
                    f['69'] = inputs['ss_withheld'] - f.SS_MAX

        f['72'] = f.rowsum(['62', '63', '64a', '65', '66', '67', '68', '69',
                            '70', '71'])
        if f['72'] > f['61']:
            f['73'] = f['72'] - f['61']
        else:
            f['76'] = f['61'] - f['72']


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
        w['15'] = w['14'] * .15
        w['16'] = f.tax_worksheet(inputs['status'], w['7'])
        w['17'] = w['15'] + w['16']
        w['18'] = f.tax_worksheet(inputs['status'], w['1'])
        w['19'] = min(w['17'], w['18'])
        return w['19']

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
        w['4'] = math.ceil(max(0, w['2'] - w['3']) / 1000) * 1000
        w['5'] = w['4'] * .05
        if w['1'] <= w['5']:
            return None
        w['6'] = w['1'] - w['5']
        w['7'] = f['46']
        w['8'] = f.rowsum(['47', '48', '49', '50'])
        if w['7'] == w['8']:
            return None
        w['9'] = w['7'] - w['8']
        if w['6'] > w['9']:
            w['10'] = w['9']
        else:
            w['10'] = w['6']
        return w['10']

    def title(f):
        return 'Form 1040'
