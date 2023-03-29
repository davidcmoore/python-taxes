#!/usr/bin/env python3
#
# Compute and plot marginal tax rates (regular and LT capital gains) for a
# married couple filing a joint return. We assume:
#  - No children
#  - Income comes entirely from wages
#  - Each spouse earns exactly half the wages
#  - State tax is paid at a rate of 9% on the income
#
# The payroll tax (social security and medicare) is not included in
# the computed marginal rates although we do include the "Additional
# Medicare Tax" in these rates.

import copy
from f1040 import F1040
from f1040sse import SS_WAGE_LIMIT
from form import FilingStatus
import matplotlib.pyplot as plt

template = {
    'status': FilingStatus.JOINT,
    'exemptions': 2,
    'disable_rounding': True,
}

MEDICARE_RATE = .0145

def compute_with_income(template, income, capital_gains):
    inputs = copy.deepcopy(template)
    inputs['wages']          = [income, income]
    inputs['wages_medicare'] = [income, income]
    inputs['medicare_withheld'] = [income * MEDICARE_RATE,
                                   income * MEDICARE_RATE]
    ss = min(SS_WAGE_LIMIT, income)
    inputs['wages_ss'] = [ss, ss]
    inputs['state_withholding'] = (2 * income + capital_gains) * .09
    inputs['capital_gain_long'] = capital_gains
    return F1040(inputs)


max_income = 700000
step = 1000
inc = 10

incomes = []
rates = []
capgain_rates = []

for x in range(0, max_income, step):
    fbase = compute_with_income(template, x/2, 0)
    fnext = compute_with_income(template, (x + inc) / 2, 0)
    fcapgain = compute_with_income(template, x/2, inc)

    rate         = float(fnext['24'] - fbase['24']) / inc
    capgain_rate = float(fcapgain['24'] - fbase['24']) / inc

    print('%6d %6d %5.3f %5.3f' % (x, fbase['24'], rate, capgain_rate))
    incomes.append(x)
    rates.append(rate)
    capgain_rates.append(capgain_rate)

plt.plot(incomes, rates, label='Ordinary Income')
plt.plot(incomes, capgain_rates, label='LT Cap Gains')
plt.title('Marginal Rates of Fed. Income Tax for Joint Return')
plt.xlabel('Income')
plt.ylabel('Marginal Rate')
plt.legend(loc=4)
plt.grid(True)
plt.show()
