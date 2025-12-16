from form import Form, FilingStatus

class F8995(Form):
    """Form 8995, Qualified Business Income Deduction Simplified Computation"""
    def __init__(f, inputs, f1040, sched_d):
        super(F8995, f).__init__(inputs)

        f['2'] = f1040['s1_3'] - (f1040.rowsum(['s1_1[567]']) or 0) \
                   + inputs.get('additional_qbi', 0)
        f['4'] = max(0, f['2'] + f['3'])
        f['5'] = f['4'] * 0.20
        f['6'] = inputs.get('section_199A_dividends')
        f['7'] = inputs.get('qualified_REIT_net_carryforward')
        f['8'] = max(0, f['6'] + f['7'])
        f['9'] = f['8'] * 0.2
        f['10'] = f['5'] + f['9']
        f['11'] = f1040['11'] - f1040['12']
        if sched_d.mustFile():
            f['12'] = f1040['3a'] + max(0, min(sched_d['15'], sched_d['16']))
        else:
            f['12'] = f1040['3a'] + f1040['7']
        f['13'] = max(0,f['11'] - f['12'])
        f['14'] = f['13'] * 0.20
        f['15'] = min(f['10'], f['14'])
        if f['15']:
            f.must_file = True
        f['16'] = min(f['2'] + f['3'], 0.)
        f['17'] = min(f['6'] + f['7'], 0.)

    def title(self):
        return 'Form 8995'
