from form import Form, FilingStatus

class F8995A(Form):
    """Form 8995A, Qualified Business Income Deduction"""
    def __init__(f, inputs, f1040, sched_d):
        super(F8995A, f).__init__(inputs)
        # TODO: Parts I, II, and III

        f['28'] = inputs.get('section_199A_dividends')
        f['30'] = max(0, f['28'] + f['29'])
        f['31'] = f['30'] * 0.20
        f['32'] = f.rowsum(['27', '31'])
        f['33'] = f1040['11'] - f1040['12']

        if sched_d.mustFile():
            f['34'] = f1040['3a'] + max(0, min(sched_d['15'], sched_d['16']))
        else:
            f['34'] = f1040['3a'] + f1040['7']

        f['35'] = max(0, f['33'] - f['34'])
        f['36'] = f['35'] * 0.20
        f['37'] = min(f['32'], f['36'])
        f.comment['39'] = 'Total QBI deduction'
        f['39'] = f.rowsum(['37', '38'])
        f.comment['40'] = 'REIT and PTP carryforward'
        f['40'] = min(0, f['28'] + f['29'])

        if f['39'] or f['40']:
            f.must_file = True

    def title(self):
        return 'Form 8995A'
