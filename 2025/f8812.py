import math
from form import Form, FilingStatus

class F8812(Form):
    """Schedule 8812, Credits for Qualifying Children and Other Dependents"""
    def __init__(f, inputs, f1040):
        super(F8812, f).__init__(inputs)
        if not inputs.get('qualifying_children'):
            return
        f['1'] = f1040['11a']
        f['2d'] = f.rowsum(['2a', '2b', '2c'])
        f['3'] = f.rowsum(['1', '2d'])
        f['4'] = inputs.get('qualifying_children')
        f['5'] = f['4'] * 2200
        f['7'] = f['6'] * 500
        f['8'] = f.rowsum(['5', '7'])
        if inputs['status'] == FilingStatus.JOINT:
            f['9'] = 400000
        else:
            f['9'] = 200000
        if f.disable_rounding:
            f['10'] = max(0, f['3'] - f['9'])
        else:
            f['10'] = math.ceil(max(0, f['3'] - f['9']) / 1000.0) * 1000
        f['11'] = f['10'] * .05
        f['12'] = max(0, f['8'] - f['11'])

        f.props['child_credit_phaseout'] = f['10'] > 0 and f['12'] > 0

        if f['12']:
            f['13'] = f1040['18'] - (f1040.rowsum(['s3_[1-4]', 's3_5b',
                           's3_6d', 's3_6f', 's3_6l', 's3_6m']) or 0)
        else:
            f['13'] = 0
        f['14'] = min(f['12'], f['13'])
        if f['14']:
            f.must_file = True

    def part2(f, inputs, f1040):
        if f['12'] <= f['14']:
            return

        f['16a'] = f['12'] - f['14']
        f['16b'] = f['4'] * 1700

        if f['16b'] == 0:
            return

        f['17'] = min(f['16a'], f['16b'])
        f['18a'] = f1040['1z'] + f1040['1i'] + inputs.get('business_income', 0) \
                   - f1040['s1_8'] - f1040['s1_15']
        f['18b'] = f1040['1i']
        f['19'] = max(0, f['18a'] - 2500)
        f['20'] = f['19'] * 0.15
        if f['16b'] >= 5100 and f['17'] > f['20']:
            f['21'] = f.spouseSum(inputs, 'medicare_withheld') \
                      + f.spouseSum(inputs, 'ss_withheld')
            f['22'] = f1040.rowsum(['s1_15', 's2_5', 's2_6', 's2_13'])
            f['23'] = f.rowsum(['21', '22'])
            f['24'] = f1040.rowsum(['27a', 's3_11'])
            f['25'] = max(0, f['23'] - f['24'])
            f['26'] = max(f['20'], f['25'])
            f['27'] = min(f['17'], f['26'])
        else:
            f['27'] = min(f['17'], f['20'])

        if f['27']:
            f.must_file = True

    def title(self):
        return 'Schedule 8812'
