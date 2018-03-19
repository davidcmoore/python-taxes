from form import Form, FilingStatus

class F1040sa(Form):
    LIMITS = [261500, 313800, 156900, 287650, 313800]

    def __init__(f, inputs, f1040):
        super(F1040sa, f).__init__(inputs)
        if f['1']:
            f['2'] = f1040['38']
            f['3'] = f['2'] * .075
            f['4'] = max(0, f['1'] - f['3'])
        f['5'] = inputs['state_withholding'] + \
                 inputs.get('extra_state_tax_payments', 0)
        f['9'] = f.rowsum(['5', '6', '7', '8'])
        f['15'] = f.rowsum(['10', '11', '12', '13', '14'])
        f['19'] = f.rowsum(['16', '17', '18'])
        f['24'] = f.rowsum(['21', '22', '23'])
        if '24' in f:
            f['25'] = f1040['38']
            f['26'] = f['25'] * .02
            f['27'] = max(0, f['24'] - f['26'])
        f['29'] = f.worksheet(inputs, f1040)['10']
        f.must_file = True

    def worksheet(f, inputs, f1040):
        w = {}
        w['1'] = f.rowsum(['4', '9', '15', '19', '20', '27', '28']) or 0
        # TODO: gambling, casualty, theft losses from line 28
        w['2'] = f.rowsum(['4', '14', '20']) or 0
        if w['2'] >= w['1']:
            w['10'] = w['1']
            return w
        w['3'] = w['1'] - w['2']
        w['4'] = w['3'] * .8
        w['5'] = f1040['38']
        w['6'] = f.LIMITS[inputs['status']]
        if w['6'] >= w['5']:
            w['10'] = w['1']
            return w
        w['7'] = w['5'] - w['6']
        w['8'] = w['7'] * .03
        w['9'] = min(w['4'], w['8'])
        w['10'] = w['1'] - w['9']
        return w

    def title(self):
        return 'Schedule A'
