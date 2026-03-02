from f1040sse import SS_WAGE_LIMIT
from f8959 import MEDICARE_RATE
import copy
import math

def increment_input(inputs, key, value, state_tax_rate=0):
    inputs = copy.deepcopy(inputs)

    def incv(d, k, v, maxv=math.inf):
        while type(k) == tuple:
            d = d[k[0]]
            k = k[1] if len(k) == 2 else k[1:]
        if type(d[k]) == list:
            if (d[k][0] < d[k][1]) ^ (v < 0):
                d[k][0] = min(d[k][0] + v, maxv)
            else:
                d[k][1] = min(d[k][1] + v, maxv)
        else:
            d[k] = min(d[k] + v, maxv)

    incv(inputs, key, value)
    if key == 'wages':
        incv(inputs, 'wages_medicare', value)
        incv(inputs, 'wages_ss', value, maxv=SS_WAGE_LIMIT)
        incv(inputs, 'medicare_withheld', value * MEDICARE_RATE)

    if state_tax_rate:
        incv(inputs, 'state_withholding', value * state_tax_rate)

    return inputs

def marginal_tax_rate(form, inputs, key, state_tax_rate=0):
    inputs = copy.deepcopy(inputs)
    inputs['disable_rounding'] = True

    increment = 10.0

    f1 = form(inputs)
    f2 = form(increment_input(inputs, key, increment, state_tax_rate))

    return (f2.tax_due() - f1.tax_due()) / increment, f1, f2

def sweep_input_for_marginal_rates(form, inputs, key, minv, maxv, state_tax_rate=0, print_prop_diffs=True):
    prev_props = None
    step = 1000
    input_vals = []
    rates = []

    if 'capital_gain' not in key:
        d = inputs
        k = key
        while type(k) == tuple:
            d = d[k[0]]
            k = k[1] if len(k) == 2 else k[1:]
        if type(d[k]) == list:
            minv = max(minv, -max(d[k][0], d[k][1]))
        else:
            minv = max(minv, -d[k])

    minv = math.ceil(minv / step) * step

    for x in range(minv, maxv, step):
        inputs2 = increment_input(inputs, key, x, state_tax_rate)
        rate, fbase, _ = marginal_tax_rate(form, inputs2, key, state_tax_rate)

        if print_prop_diffs:
            if prev_props:
                if fbase.printPropDiffs(prev_props, f'{x-step}: '):
                    print('  rate: %5.3f' % rate)
            else:
                print('  rate: %5.3f' % rate)
        prev_props = fbase.props

        input_vals.append(x)
        rates.append(rate)

    return input_vals, rates
