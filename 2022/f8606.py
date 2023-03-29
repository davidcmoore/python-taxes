from form import Form, FilingStatus

class F8606(Form):
    """Form 8606, Nondeductible IRAs"""
    def __init__(f, inputs, spouse):
        super(F8606, f).__init__(inputs, init_idx=spouse)
        f.spouse = spouse
        f.comment['2'] = 'Starting basis in traditional IRAs'
        f['3'] = f['1'] + f['2']
        f['5'] = f['3'] - f['4']
        f['9'] = f.rowsum(['6', '7', '8'])
        f['10'] = min(10000, f['5'] * 10000.0 / f['9'])
        f['11'] = f['8'] * f['10'] / 10000.0
        f['12'] = f['7'] * f['10'] / 10000.0
        f['13'] = f['11'] + f['12']
        f.comment['14'] = 'Ending basis in traditional IRAs'
        f['14'] = f['3'] - f['13']
        f['15a'] = f['7'] - f['12']
        f.comment['15c'] = 'Taxable Distribution'
        f['15c'] = f['15a'] - f['15b']
        f['16'] = f['8']
        f['17'] = f['11']
        f.comment['18'] = 'Taxable Conversion'
        f['18'] = f['16'] - f['17']
        # TODO: Roth IRA distributions
        f.must_file = True
        return

    def title(self):
        if self.spouse is not None:
            return 'Form 8606 [%d]' % self.spouse
        else:
            return 'Form 8606'
