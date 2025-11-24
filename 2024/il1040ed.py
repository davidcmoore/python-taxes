
from form import Form

class IL1040ED(Form):
    """
    Illinois Schedule ED: Education Expense Credit (2024)
    """
    def __init__(f, inputs, il1040):
        super(IL1040ED, f).__init__(inputs)
        f.must_file = True
        f.addForm(f)

        # Line 1: Qualified education expenses
        f.comment['1'] = 'Qualified education expenses'
        f['1'] = inputs.get('qualified_education_expenses', 0)

        # Line 2: Education expense credit (official formula)
        f.comment['2'] = 'Education expense credit (see instructions)'
        # Official formula: 25% of excess expenses over $250, max $750
        excess = max(0, f['1'] - 250)
        f['2'] = min(int(round(excess * 0.25)), 750)
