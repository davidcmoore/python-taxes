
from form import Form

class IL1040IN(Form):
    """
    Illinois Schedule IN: Interest and Dividends (2024)
    """
    def __init__(f, inputs, il1040):
        super(IL1040IN, f).__init__(inputs)
        f.must_file = True
        f.addForm(f)

        # Line 1: Taxable interest
        f.comment['1'] = 'Taxable interest'
        f['1'] = inputs.get('taxable_interest', 0)

        # Line 2: Tax-exempt interest
        f.comment['2'] = 'Tax-exempt interest'
        f['2'] = inputs.get('tax_exempt_interest', 0)

        # Line 3: Ordinary dividends
        f.comment['3'] = 'Ordinary dividends'
        f['3'] = inputs.get('dividends', 0)

        # Line 4: Qualified dividends
        f.comment['4'] = 'Qualified dividends'
        f['4'] = inputs.get('qualified_dividends', 0)
