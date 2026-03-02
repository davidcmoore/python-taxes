from form import Form, FilingStatus

class F1040sa(Form):
    def __init__(f, inputs, f1040):
        super(F1040sa, f).__init__(inputs)
        if f['1']:
            f['2'] = f1040['11b']
            f['3'] = f['2'] * .075
            f['4'] = max(0, f['1'] - f['3'])
        f['5a'] = inputs.get('state_withholding', 0) + \
                  inputs.get('extra_state_tax_payments', 0)
        f['5d'] = f.rowsum(['5a', '5b', '5c'])
        limit = f.salt_cap_limit(inputs, f1040)
        f.comment['5e'] = 'SALT deduction'
        f['5e'] = min(f['5d'], limit)
        f.props['SALT_capped'] = (f['5d'] > limit)
        f['7'] = f.rowsum(['5e', '6'])
        f['8e'] = f.rowsum(['8a', '8b', '8c'])
        f['10'] = f.rowsum(['8e', '9'])
        f['14'] = f.rowsum(['11', '12', '13'])
        f['17'] = f.rowsum(['4', '7', '10', '14', '15', '16'])

    def salt_cap_limit(f, inputs, f1040):
        w = {}
        w['1'] = 40000
        w['2'] = f1040['11b']
        w['4'] = w['2']
        w['5'] = 250000 if inputs['status'] == FilingStatus.SEPARATE else 500000
        w['6'] = w['4'] - w['5']
        if w['6'] > 0:
            w['7'] = w['6'] * .3
            w['8'] = w['1'] - w['7']
            w['9'] = max(10000, w['8'])
            f.props['SALT_cap_phaseout'] = w['9'] > 10000
        else:
            w['9'] = w['1']
            f.props['SALT_cap_phaseout'] = False
        return w['9'] / 2 if inputs['status'] == FilingStatus.SEPARATE else w['9']

    def title(self):
        return 'Schedule A'
