from form import Form, FilingStatus

class F8801(Form):
    """Form 8801, Credit for Prior Year Minimum Tax"""
    def __init__(f, inputs, f1040, f6251):
        super(F8801, f).__init__(inputs)
        f['21'] = inputs.get('prior_amt_credit')
        if not f['21']:
            return

        f.must_file = True
        f['22'] = max(0, f1040['16'] + f1040['s2_2'] - \
            (f1040.rowsum(['19', 's3_[1-4]', 's3_5[a-b]', 's3_6[acdefghijlmz]']) or 0))
        f['23'] = f6251.get('9')
        f['24'] = max(0, f['22'] - f['23'])
        f.comment['25'] = 'Minimum tax credit'
        f['25'] = min(f['21'], f['24'])
        if f['25']:
            f6251.must_file = True
        f.comment['26'] = 'Credit carryforward to 2024'
        f['26'] = f['21'] - f['25']

    def title(self):
        return 'Form 8801 (for 2023 filing)'
