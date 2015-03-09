from form import Form, FilingStatus

class F8960(Form):
    """Form 8960, Net Investment Income Tax"""
    THRESHOLDS = [200000, 250000, 125000, 200000, 250000]
    def __init__(f, inputs, f1040, sched_a):
        super(F8960, f).__init__(inputs)
        f['1'] = f1040.get('8a')
        f['2'] = f1040.get('9a')
        # TODO: annuities
        f['4a'] = f1040.get('17')
        f['4c'] = f.rowsum(['4a', '4b'])
        f['5a'] = f1040.rowsum(['13', '14'])
        f['5d'] = f.rowsum(['5a', '5b', '5c'])
        f['8'] = f.rowsum(['1', '2', '3', '4c', '5d', '6', '7'])
        if sched_a:
            # This is one example of a "reasonable method allocation" but
            # not the only way.
            # Note: this only works for state income tax, not sales tax
            f['9b'] = f['8'] * sched_a['5'] / f1040['38']
        f['9d'] = f.rowsum(['9a', '9b', '9c'])
        f['11'] = f.rowsum(['9d', '10'])
        f['12'] = max(0, f['8'] - f['11'])
        f['13'] = f1040['38']
        f['14'] = f.THRESHOLDS[inputs['status']]
        f['15'] = max(0, f['13'] - f['14'])
        f['16'] = min(f['12'], f['15'])
        if f['16']:
            f['17'] = f['16'] * .038
            f.must_file = True
        return

    def title(self):
        return 'Form 8960'
