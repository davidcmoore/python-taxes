
from form import Form

class IL1040M(Form):
    """
    Illinois Schedule M: Other Additions and Subtractions (2024)
    """
    def __init__(f, inputs, il1040):
        super(IL1040M, f).__init__(inputs)
        f.must_file = True
        f.addForm(f)

        # Additions (lines 1-20, see official Schedule M)
        f.comment['1'] = 'Recapture of deductions (e.g., bonus depreciation)'
        f['1'] = inputs.get('recapture_bonus_depr', 0)
        f.comment['2'] = 'Other additions (see instructions)'
        f['2'] = inputs.get('other_additions', 0)
        # ... add more lines as needed for all official additions ...

        # Subtractions (lines 21-40, see official Schedule M)
        f.comment['21'] = 'Retirement income subtraction'
        f['21'] = inputs.get('retirement_income_sub', 0)
        f.comment['22'] = 'Social Security income subtraction'
        f['22'] = inputs.get('social_security_sub', 0)
        f.comment['23'] = 'Other subtractions (see instructions)'
        f['23'] = inputs.get('other_subtractions', 0)
        # ... add more lines as needed for all official subtractions ...

        # Total additions
        f.comment['A'] = 'Total Additions'
        f['A'] = sum(f[i] for i in ['1','2']) # expand as needed
        # Total subtractions
        f.comment['B'] = 'Total Subtractions'
        f['B'] = sum(f[i] for i in ['21','22','23']) # expand as needed

        # Net other subtractions for IL1040 line 7
        f.comment['2'] = 'Other subtractions for IL1040 line 7'
        f['2'] = f['B']
