
from form import Form

class IL1040529(Form):
    """
    Illinois Schedule 529: IL 529 Plan Deduction (2024)
    """
    def __init__(f, inputs, il1040):
        super(IL1040529, f).__init__(inputs)
        f.must_file = True
        f.addForm(f)

        # Line 1: IL 529 plan contribution
        f.comment['1'] = 'IL 529 plan contribution'
        f['1'] = inputs.get('il_529_contribution', 0)

        # Line 2: 529 deduction allowed (official max deduction)
        f.comment['2'] = '529 deduction allowed (max $10,000 single, $20,000 joint)'
        max_ded = 20000 if inputs['status'] == 1 else 10000
        f['2'] = min(f['1'], max_ded)
