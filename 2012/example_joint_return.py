#!/usr/bin/env python
#
# Example of a married couple filing jointly. Each spouse has an income
# of 100k. Also, the first spouse has some investment income and
# business (Schedule C) income.
#
# Due to high state taxes paid (see Schedule A) this couple will pay AMT.
# Form 6251 is shown in the output.
#
# A balance is owed on the return.
#

from f1040 import F1040
from form import FilingStatus

# Note that some of the quantities below we need to list separately for each
# spouse in an array.

inputs = {
    'status': FilingStatus.JOINT,
    'exemptions': 2,
    'wages':    [100000.00, 100000.00], # W2 box 1
    'wages_ss': [100000.00, 100000.00], # W2 box 3
    'withholding':        37000.00, # W2 box 2
    'ss_withheld':  [4200.00, 4200.00], # W2 box 4
    'taxable_interest':    1500.00,
    'tax_exempt_interest':  700.00,
    'dividends':           3000.00,
    'qualified_dividends': 2000.00,
    'capital_gain_dist':    500.00,
    'capital_gain_long':   5000.00,
    'business_income':   [5000.00, 0.00],

    # Extra items for schedule A
    'F1040sa' : {
                  '5' : 25000,   # state tax paid
                 '16' : 500,     # charitable contributions
                },
}

f = F1040(inputs)
f.printAllForms()
