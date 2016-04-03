#!/usr/bin/env python
#
# Example of a married couple filing jointly. Each spouse has an income
# of 100k. Also, the first spouse has some investment income and
# business (Schedule C) income.
#
# A balance is owed on the return.
#
# On the state return, a refund is due.
#

from f1040 import F1040
from ca540 import CA540
from form import FilingStatus

# Note that some of the quantities below we need to list separately for each
# spouse in an array. Everything else we just need a total.

inputs = {
    'status': FilingStatus.JOINT,
    'exemptions': 2,
    'wages':             [100000.00, 100000.00], # W2 box 1
    'withholding':                    37000.00,  # W2 box 2
    'wages_ss':          [100000.00, 100000.00], # W2 box 3
    'ss_withheld':       [  6200.00,   6200.00], # W2 box 4
    'wages_medicare':    [100000.00, 100000.00], # W2 box 5
    'medicare_withheld': [  1450.00,   1450.00], # W2 box 6
    'state_withholding':              18000.00,  # W2 box 17

    # These are other state tax payments made in the tax year not included in
    # 'state_withholding' that are deductible on schedule A:
    'extra_state_tax_payments': 3000.00,

    'taxable_interest':    1500.00,
    'tax_exempt_interest':  700.00,
    'dividends':           3000.00,
    'qualified_dividends': 2000.00,
    'capital_gain_dist':    500.00,
    'capital_gain_long':   5000.00,
    'business_income':   [5000.00, 0.00],

    # Extra items for schedule A
    'F1040sa' : {
                 '16' : 500, # charitable contributions
                },
}

f = F1040(inputs)
f.printAllForms()
print('')
ca = CA540(inputs, f)
ca.printAllForms()
