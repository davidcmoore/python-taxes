
from form import Form

class IL1040ICR(Form):
    """
    Illinois Schedule ICR: Illinois Credits (2024)
    """
    def __init__(f, inputs, il1040):
        super(IL1040ICR, f).__init__(inputs)
        f.must_file = True
        f.addForm(f)

        # Line 1: Property tax credit
        f.comment['1'] = 'Property tax credit (see instructions)'
        f['1'] = inputs.get('property_tax_credit', 0)

        # Line 2: K-12 education expense credit
        f.comment['2'] = 'K-12 education expense credit'
        f['2'] = inputs.get('education_expense_credit', 0)

        # Line 3: IL 529 plan contribution credit
        f.comment['3'] = 'IL 529 plan contribution credit'
        f['3'] = inputs.get('il_529_credit', 0)

        # Line 4: Total credits
        f.comment['4'] = 'Total credits (add lines 1-3)'
        f['4'] = f['1'] + f['2'] + f['3']
