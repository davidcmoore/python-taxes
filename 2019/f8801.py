from form import Form, FilingStatus
# NOT FINAL for 2019

class F8801(Form):
    """Form 8801, Credit for Prior Year Minimum Tax"""
    def __init__(f, inputs, f1040, f6251):
        super(F8801, f).__init__(inputs)
        f['21'] = inputs.get('prior_amt_credit')
        if not f['21']:
            return

        f.must_file = True
        f['22'] = max(0, f1040['11a'] + f1040['s46'] - \
            (f1040.rowsum(['12a', 's48', 's49', 's50', 's51', 's53', 's54']) or 0))
        f['23'] = f6251.get('9')
        f['24'] = max(0, f['22'] - f['23'])
        f.comment['25'] = 'Minimum tax credit'
        f['25'] = min(f['21'], f['24'])
        if f['25']:
            f6251.must_file = True
        f.comment['26'] = 'Credit carryforward to 2019'
        f['26'] = f['21'] - f['25']

    def title(self):
        return 'Form 8801 (for 2018 filing)'
