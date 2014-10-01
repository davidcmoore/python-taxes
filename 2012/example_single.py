#!/usr/bin/env python
#
# Example of a single person with wage income of 100k. Also some investment
# income and business (Schedule C) income.
#

from f1040 import F1040
from form import FilingStatus

inputs = {
    'status': FilingStatus.SINGLE,
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
                  '5' : 10000,   # state tax paid
                 '16' : 500,     # charitable contributions
                },
}

f = F1040(inputs)
f.printAllForms()
