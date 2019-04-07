from form import Form, FilingStatus

class F1040sa(Form):
    def __init__(f, inputs, f1040):
        super(F1040sa, f).__init__(inputs)
        if f['1']:
            f['2'] = f1040['7']
            f['3'] = f['2'] * .075
            f['4'] = max(0, f['1'] - f['3'])
        f['5a'] = inputs['state_withholding'] + \
                  inputs.get('extra_state_tax_payments', 0)
        f['5d'] = f.rowsum(['5a', '5b', '5c'])
        f['5e'] = min(f['5d'],
                5000 if inputs['status'] == FilingStatus.SEPARATE else 10000)
        f['7'] = f.rowsum(['5e', '6'])
        f['10'] = f.rowsum(['8e', '9'])
        f['14'] = f.rowsum(['11', '12', '13'])
        f['17'] = f.rowsum(['4', '7', '10', '14', '15', '16'])

    def title(self):
        return 'Schedule A'
