
from form import Form

class IL1040CR(Form):
    """
    Illinois Schedule CR: Credit for Tax Paid to Other States (2024)
    """
    def __init__(f, inputs, il1040):
        super(IL1040CR, f).__init__(inputs)
        f.must_file = True
        f.addForm(f)

        # Line 1: Tax paid to other states
        f.comment['1'] = 'Tax paid to other states'
        f['1'] = inputs.get('tax_paid_other_states', 0)

        # Line 2: IL tax credit (cannot exceed IL tax)
        f.comment['2'] = 'IL tax credit (cannot exceed IL tax)'
        f['2'] = min(f['1'], il1040['11'])
