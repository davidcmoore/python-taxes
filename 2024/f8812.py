import math
from form import Form, FilingStatus

class F8812(Form):
    """Schedule 8812, Credits for Qualifying Children and Other Dependents"""
    def __init__(f, inputs, f1040):
        super(F8812, f).__init__(inputs)
        if not inputs.get('qualifying_children'):
            return
        f['1'] = f1040['11']
        f['2d'] = f.rowsum(['2a', '2b', '2c'])
        f['3'] = f.rowsum(['1', '2d'])
        f['4'] = inputs.get('qualifying_children')
        f['5'] = f['4'] * 2000
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

        if f['12']:
            f['13'] = f1040['18'] - (f1040.rowsum(['s3_[1-4]', 's3_5b',
                           's3_6d', 's3_6f', 's3_6l', 's3_6m']) or 0)
        else:
            f['13'] = 0
        f['14'] = min(f['12'], f['13'])
        if f['14']:
            f.must_file = True

        if f['12'] > f['14']:
            raise RuntimeError('TODO: additional child tax credit')

    def title(self):
        return 'Schedule 8812'
