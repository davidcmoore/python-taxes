from form import Form

class IL1040E_EITC(Form):
    """
    Schedule IL-E/EITC implementation for 2024

    Developed by Stefano M. Canta (cantastefano@gmail.com).
    This software is provided without any warranty, express or implied.
    It is intended solely for the author's personal tax calculations and should not be relied upon for any other purpose.
    Use at your own risk.
    """
    def __init__(f, inputs, il1040):
        super(IL1040E_EITC, f).__init__(inputs)
        f.must_file = True
        f.addForm(f)

        # Line 1: Dependent exemption allowance
        f.comment['1'] = 'Dependent exemption allowance'
        f['1'] = inputs.get('dependent_care_persons', 0)*il1040.DEPENDENT_EXEMPTION

        # TODO finish IL EITC

    def title(f):
        return 'Schedule IL-E/EITC'
