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
from form import FilingStatus
import plotly.graph_objects as go
import plan

STATE_RATE = 0.09
CG = 0

template = {
    'status': FilingStatus.JOINT,
    'exemptions': 4,
    'qualifying_children': 2,
    'wages': [0, 0],
    'wages_medicare': [0, 0],
    'wages_ss': [0, 0],
    'medicare_withheld': [0, 0],
    'capital_gain_long': CG,
    'state_withholding': CG * STATE_RATE,
}

incomes = []
rates = []
capgain_rates = []
step = 1000

prev_props = None
for x in range(60000, 950000, step):
    inputs = plan.increment_input(template, 'wages', x - CG, state_tax_rate=STATE_RATE)
    rate, fbase, _ = plan.marginal_tax_rate(F1040, inputs, 'wages', state_tax_rate=STATE_RATE)
    capgain_rate, _, _ = plan.marginal_tax_rate(F1040, inputs, 'capital_gain_long', state_tax_rate=STATE_RATE)

    if prev_props:
        if fbase.printPropDiffs(prev_props, f'{x-step}: '):
            print('  rate: %5.3f   lt gain rate: %5.3f' % (rate, capgain_rate))
    prev_props = fbase.props

    #print('%6d %6d %6d %6d %5.3f %5.3f' % (x, fbase_tax, fnext_tax, fcapgain_tax, rate, capgain_rate))
    incomes.append(x)
    rates.append(max(-0.01, rate))
    capgain_rates.append(max(-0.01, capgain_rate))

fig = go.Figure()
fig.add_trace(go.Scatter(x=incomes, y=rates, name='Ordinary Income'))
fig.add_trace(go.Scatter(x=incomes, y=capgain_rates, name='LT Cap Gains'))
fig.update_layout(title='Marginal Rates of Fed. Income Tax for Joint Return',
                  xaxis=dict(title=dict(text='Income')),
                  yaxis=dict(title=dict(text='Marginal Rate')),
                  hovermode='x unified',
                 )
fig.show()
