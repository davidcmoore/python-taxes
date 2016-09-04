from form import Form, FilingStatus
import math

class F2441(Form):
    """Form 2441, Child and Dependent Care Expenses"""
    def __init__(f, inputs, sse):
        super(F2441, f).__init__(inputs)
        # Part III must be completed before Part II
        f['15'] = f['12'] + f['13'] - f['14']
        f['17'] = min(f['15'], f['16'])

        # TODO: logic for filing separately
        assert(inputs['status'] != FilingStatus.SEPARATE)
        if inputs['status'] == FilingStatus.JOINT:
            f['18'] = f.earned_income(inputs['wages'][0], sse[0])
            f['19'] = f.earned_income(inputs['wages'][1], sse[1])
        else:
            f['18'] = f['19'] = f.earned_income(inputs['wages'], sse)
        f['20'] = min(f['17'], f['18'], f['19'])
        f['21'] = 5000
        # TODO: partnership/proprietorship-provided childcare benefits
        f['22'] = 0
        f['23'] = f['15'] - f['22']
        f.comment['24'] = 'Deductible benefits'
        f['24'] = min(f['20'], f['21'], f['22'])
        f.comment['25'] = 'Excluded benefits'
        f['25'] = min(f['20'], f['21'])
        f.comment['26'] = 'Taxable benefits'
        f['26'] = max(0, f['23'] - f['25'])
        assert(f['24'] == 0)
        if f['24'] or f['25'] or f['26']:
            f.must_file = True
        f['27'] = min(inputs.get('dependent_care_persons', 0), 2) * 3000
        f['28'] = f['24'] + f['25']
        f['29'] = f['27'] - f['28']

    def part2(f, f1040):
        if f['29'] <= 0:
            return None
        f['2c'] = f['16'] - f['28']
        f['30'] = f['2c']
        f['31'] = min(f['29'], f['30'])
        f['3'] = f['31']
        f['4'] = f['18']
        f['5'] = f['19']
        f['6'] = min(f['3'], f['4'], f['5'])
        f['7'] = f1040['38']
        f['8'] = f.credit_percent(f['7'])
        f['9'] = f['6'] * f['8'] / 100.0
        f['10'] = f1040['47'] - f1040['48']
        if f['10'] <= 0:
            return None
        f['11'] = min(f['9'], f['10'])
        if f['11']:
            f.must_file = True
        return f.get('11')

    def earned_income(f, wages, sse):
        if sse.mustFile():
            return wages + (sse['A3'] or sse['B3']) - (sse['A6'] or sse['B13'])
        else:
            return wages

    def credit_percent(f, agi):
        upper = 45000
        return min(35, math.floor((upper - min(upper, agi)) / 2000.0) + 20)

    def title(self):
        return 'Form 2441'
