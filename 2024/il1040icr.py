
from form import Form

class IL1040ICR(Form):
    """
    Illinois Schedule ICR: Illinois Credits (2024)
    """
    def __init__(f, inputs, il1040):
        super(IL1040ICR, f).__init__(inputs)
        f.must_file = True
        f.addForm(f)

        f['1'] = il1040['14']
        f['2'] = il1040['15']
        f['3'] = f['1'] - f['2']

        # line 4a is given

        # TODO line 4e business credit
        f['4e'] = 0
        f['4f'] = f['4a'] - f['4e']
        f['4g'] = round(0.05*f['4f'])

        f['5'] = min(f['3'], f['4g'])
        f['6'] = f['3'] - f['5']

        # f['7a'] is given
        f['7c'] = max(0, f['7a'] - 250.)
        f['7d'] = min(750, round(0.25 * f['7c']))
        f['8'] = min(f['6'], f['7d'])
        f['9'] = f['6'] - f['8']

        # TODO section C

        f['13'] = f.rowsum(['5', '8', '11'])

    def title(f):
        return 'Schedule IL-ICR'