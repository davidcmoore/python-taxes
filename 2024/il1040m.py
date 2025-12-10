
from form import Form, FilingStatus
# from il1040 import IL1040
import re

class IL1040M(Form):
    """
    Schedule IL-M implementation for 2024

    Developed by Stefano M. Canta (cantastefano@gmail.com).
    This software is provided without any warranty, express or implied.
    It is intended solely for the author's personal tax calculations and should not be relied upon for any other purpose.
    Use at your own risk.

    Implemented inputs (keys in `inputs` dict):
        - '13a': Contributions to IL 529 accounts (float)
        - '20a': Contributions to IL ABLE accounts (float)
        - '22': U.S. Treasury bonds, bills, notes, savings bonds, and U.S. agency interest (float)
    """
    def __init__(f, inputs, il1040):
        super(IL1040M, f).__init__(inputs)
        f.must_file = True
        f.addForm(f)

        # Additions (lines 1-10, see official Schedule M)
        # Provide these lines as inputs to the form rather
        # than here, as there is nothing to calculate
        f.comment['12'] = 'Total Additions to IL income'
        f['12'] = f.rowsum(['11', '10', '[1-9]'])

        # Subtractions to income
        # Provide these lines as inputs to the form rather
        # than here, except where calculations are needed
        cap_529_contrib = 20000 if inputs['status'] == FilingStatus.JOINT else 10000
        f['13'] = min(f['13a'], cap_529_contrib)
        cap_able_contrib = 20000 if inputs['status'] == FilingStatus.JOINT else 10000
        f['20'] = min(f['20a'], cap_able_contrib)

        f['32'] = f.rowsum(['3[01]', '2[0-9]', '1[3-9]']) or None
        f['33'] = f['32'] or None

        # Line 34: Sum of lines 34a through 34z
        f['34'] = f.rowsum('34[a-z]') or None
        f['35'] = f.rowsum('35[a-f]') or None

        f.comment['42'] = 'Total Subtractions to IL income'
        f['42'] = f.rowsum(['3[3-9]', '4[01]'])
  
    def title(f):
        return 'Form IL-1040 Schedule M'
