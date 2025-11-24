
from form import Form

class IL1040BUS(Form):
    """
    Illinois Schedule BUS: Business Income (2024)
    """
    def __init__(f, inputs, il1040):
        super(IL1040BUS, f).__init__(inputs)
        f.must_file = True
        f.addForm(f)

        # Line 1: Business income
        f.comment['1'] = 'Business income'
        f['1'] = inputs.get('business_income', 0)

        # Line 2: Business deductions
        f.comment['2'] = 'Business deductions'
        f['2'] = inputs.get('business_deductions', 0)

        # Line 3: Net business income
        f.comment['3'] = 'Net business income'
        f['3'] = f['1'] - f['2']
