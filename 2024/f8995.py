from form import Form, FilingStatus

class F8995(Form):
    """Form 8995A, Qualified Business Income Deduction Simplified Computation"""
    def __init__(f, inputs, f1040, sched_d, sse):
        super(F8995, f).__init__(inputs)

        if inputs['status'] == FilingStatus.JOINT:
            f['2']  = sse[0]['3'] - sse[0]['13'] if sse[0].mustFile else 0
            f['2'] += sse[1]['3'] - sse[1]['13'] if sse[1].mustFile else 0
        else:
            f['2']  = sse['3'] - sse['13'] if sse.mustFile else 0
        f['3'] = inputs.get('qualified_business_net_carryforward')
        f['4'] = max(0, f['2'] - f['3'])
        f['5'] = f['4'] * 0.20
        f['6'] = inputs.get('section_199A_dividends')
        f['7'] = inputs.get('qualified_REIT_net_carryforward')
        f['8'] = max(0, f['6'] - f['7'])
        f['9'] = f['8'] * 0.2
        f['10'] = f['5'] + f['9']
        f['11'] = f1040['11'] - f1040['12']
        f['12'] = f1040['7'] + f1040['3a']
        f['13'] = max(0,f['11'] - f['12'])
        f['14'] = f['13'] * 0.20
        f['15'] = min(f['10'], f['14'])
        if f['15']:
            f.must_file = True

    def title(self):
        return 'Form 8995'
