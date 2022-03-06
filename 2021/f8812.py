import math
from form import Form, FilingStatus

class F8812(Form):
    """Form 8812, Credits for Qualifying Children and Other Dependents"""
    def __init__(f, inputs, f1040):
        super(F8812, f).__init__(inputs)
        if not inputs.get('qualifying_children') and \
                not inputs.get('advance_child_tax_credit'):
            return
        f.must_file = True
        f['1'] = f1040['11']
        f['2d'] = f.rowsum(['2a', '2b', '2c'])
        f['3'] = f.rowsum(['1', '2d'])
        f['4a'] = inputs.get('qualifying_children')
        f['4b'] = inputs.get('qualifying_children_under_6')
        f['4c'] = f['4a'] - f['4b']
        f['5'] = f.line_5_worksheet(inputs)
        f['7'] = f['6'] * 500
        f['8'] = f.rowsum(['5', '7'])
        if inputs['status'] == FilingStatus.JOINT:
            f['9'] = 400000
        else:
            f['9'] = 200000
        f['10'] = math.ceil(max(0, f['3'] - f['9']) / 1000.0) * 1000
        f['11'] = f['10'] * .05
        f['12'] = max(0, f['8'] - f['11'])

        f['14a'] = min(f['7'], f['12'])
        f['14b'] = f['12'] - f['14a']
        if f['14a']:
            f['14c'] = f1040['18'] - (f1040.rowsum(['s3_1', 's3_2', 's3_3',
                                                   's3_4', 's3_6l']) or 0)
        else:
            f['14c'] = 0
        f['14d'] = min(f['14a'], f['14c'])
        f['14e'] = f.rowsum(['14b', '14d'])
        f['14f'] = inputs.get('advance_child_tax_credit', 0)
        f['14g'] = max(0, f['14e'] - f['14f'])
        f['14h'] = min(f['14d'], f['14g'])
        f['14i'] = f['14g'] - f['14h']

        if not inputs.get('advance_child_tax_credit') or f['14g']:
            return

        f['28a'] = f['14f']
        f['28b'] = f['14e']
        f['29'] = f['28a'] - f['28b']
        if not f['29']:
            return
        f['30'] = inputs.get('qualifying_children')
        f['31'] = min(f['4a'], f['30'])
        f['32'] = f['30'] - f['31'] # **
        THRESHOLDS = [40000, 60000, 40000, 50000, 60000]
        f['33'] = THRESHOLDS[inputs['status']]
        f['34'] = max(0, f['3'] - f['33'])
        f['35'] = f['33']
        f['36'] = min(1.0, f['34'] / f['35']) * 1000
        f['37'] = f['32'] * 2000
        f['38'] = f['37'] * f['36'] / 1000.0
        f['39'] = f['37'] - f['38']
        f['40'] = max(0, f['29'] - f['39'])

    def line_5_worksheet(f, inputs):
        MAX_CREDITS = [6250, 12500, 6250, 4375, 2500]
        THRESHOLDS = [75000, 150000, 75000, 112500, 150000]
        w = {}
        w['1'] = f['4b'] * 3600
        w['2'] = f['4c'] * 3000
        w['3'] = w['1'] + w['2']
        w['4'] = f['4a'] * 2000
        w['5'] = w['3'] - w['4']
        w['6'] = MAX_CREDITS[inputs['status']]
        w['7'] = min(w['5'], w['6'])
        w['8'] = THRESHOLDS[inputs['status']]
        w['9'] = math.ceil(max(0, f['3'] - w['8']) / 1000.0) * 1000
        w['10'] = w['9'] * .05
        w['11'] = min(w['7'], w['10'])
        w['12'] = w['3'] - w['11']
        return w['12']

    def title(self):
        return 'Form 8812'
