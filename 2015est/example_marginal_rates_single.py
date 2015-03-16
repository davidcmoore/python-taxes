#!/usr/bin/env python
#
# Compute and plot marginal tax rates (regular and LT capital gains) for a
# single person. We assume:
#  - No dependents
#  - Income comes entirely from wages
#  - State tax is paid at a rate of 9% on the income
#
# The payroll tax (social security and medicare) is not included in
# the computed marginal rates although we do include the "Additional
# Medicare Tax" in these rates.

import copy
from f1040 import F1040
from form import FilingStatus
import matplotlib.pyplot as plt

template = {
    'status': FilingStatus.SINGLE,
    'exemptions': 1,
    'disable_rounding': True,
}

SOCIAL_SECURITY_MAX = 117000
MEDICARE_RATE = .0145

def compute_with_income(template, income, capital_gains):
    inputs = copy.deepcopy(template)
    inputs['wages']          = income
    inputs['wages_medicare'] = income
    inputs['medicare_withheld'] = income * MEDICARE_RATE
    inputs['wages_ss'] = min(SOCIAL_SECURITY_MAX, income)
    inputs['state_withholding'] = (income + capital_gains) * .09
    inputs['capital_gain_long'] = capital_gains
    return F1040(inputs)


max_income = 700000
step = 1000
inc = 10

incomes = []
rates = []
capgain_rates = []

for x in xrange(0, max_income, step):
    fbase = compute_with_income(template, x, 0)
    fnext = compute_with_income(template, x + inc, 0)
    fcapgain = compute_with_income(template, x, inc)

    rate         = float(fnext['63'] - fbase['63']) / inc
    capgain_rate = float(fcapgain['63'] - fbase['63']) / inc

    print('%6d %6d %5.3f %5.3f' % (x, fbase['63'], rate, capgain_rate))
    incomes.append(x)
    rates.append(rate)
    capgain_rates.append(capgain_rate)

plt.plot(incomes, rates, label='Ordinary Income')
plt.plot(incomes, capgain_rates, label='LT Cap Gains')
plt.title('Marginal Rates of Fed. Income Tax for Single Filer')
plt.xlabel('Income')
plt.ylabel('Marginal Rate')
plt.legend(loc=4)
plt.grid(True)
plt.show()
