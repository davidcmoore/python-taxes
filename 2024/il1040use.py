
from form import Form

class IL1040USE(Form):
    """
    Illinois Schedule USE: Use Tax (2024)
    """
    def __init__(f, inputs, il1040):
        super(IL1040USE, f).__init__(inputs)
        f.must_file = True
        f.addForm(f)

        # Line 1: Use tax due
        f.comment['1'] = 'Use tax due'
        f['1'] = inputs.get('use_tax_due', 0)
