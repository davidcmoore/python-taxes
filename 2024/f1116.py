from form import Form, FilingStatus
import math

class F1116(Form):
    """Form 1116, Foreign Tax Credit"""
    def __init__(f, inputs, f1040, sched_a, sched_d):
        super(F1116, f).__init__(inputs)

        f.must_file = True
        # This software only supports Form 1116 for claiming a foreign
        # tax credit on distributions from a regulated investment company.
        f.comment['1a'] = 'Gross foreign income'
        f['1a'] = inputs.get('foreign_investment_income')

        # We don't yet handle the cases of adjusting qualified dividends
        # in the case of high income, or dealing with itemized deductions
        # allocatable to foreign source income.
        assert(f['1a'] < 20000)
        line5 = f1040.div_cap_gain_tax_worksheet(inputs, sched_d)['5']
        if inputs['status'] in [FilingStatus.JOINT, FilingStatus.WIDOW]:
            assert(line5 < 383900)
        else:
            assert(line5 < 191950)

        assert(not sched_a.mustFile())

        f['3a'] = f1040['12']
        f['3b'] = f1040['s1_26'] - (f1040.rowsum(['s1_1[125]', 's1_20']) or 0)
        f['3c'] = f.rowsum(['3a', '3b'])
        f['3d'] = inputs.get('foreign_investment_income')

        # Gross income adds back business expenses and capital losses to total income
        gross_income = f1040['9'] + (f.spouseSum(inputs, 'business_expenses') or 0)
        if sched_d.mustFile():
            assert(inputs.get('capital_gain_short', 0) >= 0)
            assert(inputs.get('capital_gain_long', 0) >= 0)
            gross_income += inputs.get('capital_loss_short', 0) + inputs.get('capital_loss_long', 0) \
                             - inputs.get('capital_gain_carryover_short', 0) \
                             - inputs.get('capital_gain_carryover_long', 0) \
                             - f1040['7'] + sched_d['16']

        f['3e'] = gross_income
        f['3f'] = f['3d'] / f['3e'] * 10000
        f['3g'] = f['3c'] * f['3f'] / 10000
        if f['3d'] > 5000 and sched_a['8e']:
            f['4a'] = sched_a['8e'] * f['3f'] / 10000
        f.comment['6'] = 'Deductions and losses'
        f['6'] = f.rowsum(['2', '3g', '4[ab]', '5'])
        f['7'] = f['1a'] - f['6']
        f.comment['8'] = 'Foreign tax paid'
        f['8'] = inputs.get('foreign_tax')
        f['9'] = f['8']
        f.comment['10'] = 'Carryover from other years'
        f['10'] = inputs.get('foreign_tax_carryover')
        f['11'] = f.rowsum(['9', '10'])
        f.comment['14'] = 'Foreign taxes available for credit'
        f['14'] = f.rowsum(['11', '12', '13'])
        f['15'] = f['7']
        f['17'] = f.rowsum(['15', '16'])
        if f['17'] <= 0:
            return

        f['18'] = f1040['15']
        f['19'] = min(1, f['17'] / f['18']) * 10000
        f['20'] = f1040.rowsum(['16', 's2_1z'])
        f['21'] = f['20'] * f['19'] / 10000
        f['23'] = f.rowsum(['21', '22'])
        f['24'] = min(f['14'], f['23'])
        f['33'] = f['24']
        f.comment['35'] = 'Foreign tax credit'
        f['35'] = f['33'] - f['34']

    def title(self):
        return 'Form 1116'
