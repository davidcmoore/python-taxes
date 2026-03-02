from form import Form, FilingStatus

class F8889(Form):
    """Form 8889, Health Savings Accounts (HSAs)"""
    def __init__(f, inputs):
        super(F8889, f).__init__(inputs)
        # TODO: spouses with separate HSAs
        f['5'] = max(0, f['3'] - f['4'])
        f['6'] = f['5']
        f['8'] = f.rowsum(['6', '7'])
        f['11'] = f.rowsum(['9', '10'])
        f['12'] = max(0, f['8'] - f['11'])
        f.comment['13'] = 'HSA Deduction'
        f['13'] = min(f['2'], f['12'])
        assert round(f['2']) <= round(f['13'])

        f['14c'] = f['14a'] - f['14b']
        f.comment['16'] = 'Taxable HSA distributions'
        f['16'] = max(0, f['14c'] - f['15'])
        f.comment['17b'] = 'Additional 20% tax'
        f['17b'] = f['16'] * .20

        f.comment['20'] = 'Total Income'
        f['20'] = f.rowsum(['18', '19'])
        f.comment['21'] = 'Additional tax'
        f['21'] = f['20'] * .10 or None

        if f['2'] or f['11'] or f['14a'] or f['20']:
            f.must_file = True

    def title(self):
        return 'Form 8889'
