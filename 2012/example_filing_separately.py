#!/usr/bin/env python
#
# Example of a married couple filing separately. Each spouse has an income
# of 100k. Also, the first spouse has some investment income and
# business (Schedule C) income.
#
# First spouse will be subject to AMT as seen in the results (form 6251
# gets created).
#
# Both spouses are owed refunds.
#

from f1040 import F1040
from form import FilingStatus

print('First Return:')

inputs = {
    'status': FilingStatus.SEPARATE,
    'exemptions': 1,
    'wages':    100000.00, # W2 box 1
    'wages_ss': 100000.00, # W2 box 3
    'withholding':        24000.00, # W2 box 2
    'ss_withheld':         4200.00, # W2 box 4
    'taxable_interest':    1500.00,
    'tax_exempt_interest':  700.00,
    'dividends':           3000.00,
    'qualified_dividends': 2000.00,
    'capital_gain_dist':    500.00,
    'capital_gain_long':   5000.00,
    'business_income':     5000.00,

    # Extra items for schedule A
    'F1040sa' : {
                  '5' : 15000,   # state tax paid
                 '16' : 500,     # charitable contributions
                },
}

f = F1040(inputs)
f.printAllForms()

print('Second Return:')

inputs = {
    'status': FilingStatus.SEPARATE,
    'exemptions': 1,
    'wages':    100000.00, # W2 box 1
    'wages_ss': 100000.00, # W2 box 3
    'withholding':        20000.00,     # W2 box 2
    'ss_withheld': 4200.00,  # W2 box 4
}

f = F1040(inputs)
f.printAllForms()
