from form import Form

class F1040sa(Form):
    def __init__(f, inputs, f1040):
        super(F1040sa, f).__init__(inputs)
        if f['1']:
            f['2'] = f1040['38']
            f['3'] = f['2'] * .075
            f['4'] = max(0, f['1'] - f['3'])
        f['9'] = f.rowsum(['5', '6', '7', '8'])
        f['15'] = f.rowsum(['10', '11', '12', '13', '14'])
        f['19'] = f.rowsum(['16', '17', '18'])
        f['24'] = f.rowsum(['21', '22', '23'])
        if '24' in f:
            f['25'] = f1040['38']
            f['26'] = f['25'] * .02
            f['27'] = max(0, f['24'] - f['26'])
        f['29'] = f.rowsum(['4', '9', '15', '19', '20', '27', '28'])
        f.must_file = True

    def title(self):
        return 'Schedule A'
