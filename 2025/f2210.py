from form import Form

class F2210(Form):
    def __init__(f, inputs, f1040):
        super(F2210, f).__init__(inputs)
        f.addForm(f)

        f['1'] = f1040['22']
        f['2'] = f1040.rowsum(['s2_(4|8|9|11|12|14|15|16|17[acdefghijlz]|19)'])
        f['3'] = f1040.rowsum(['27a', '28', '29', 's3_(9|12|13b)'])
        f['4'] = f.rowsum(['1', '2', '3'])
        if f['4'] < 1000:
            return

        f['5'] = f['4'] * .9
        f['6'] = f1040.rowsum(['25d', 's3_11'])
        f['7'] = f['4'] - f['6']
        if f['7'] < 1000:
            return
        if 'safe_harbor_tax' in inputs:
            f['8'] = inputs['safe_harbor_tax']
            f['9'] = min(f['5'], f['8'])
        else:
            f['9'] = f['5']

        if f['9'] <= f['6']:
            return

        overpayment = 0
        underpayment = 0
        for c in ['a', 'b', 'c', 'd']:
            period = ord(c) - ord('a')
            # TODO: Annualized income
            f['10'+c] = 0.25 * f['9']
            if 'withholding_by_period' in inputs:
                total = sum(inputs['withholding_by_period'])
                if abs(total - inputs['withholding']) >= 0.01:
                    raise RuntimeError(f"By-period withholding is {total} but input is {inputs['withholding']}")
                withholding = inputs['withholding_by_period'][period]
                f.must_file = True
            else:
                withholding = 0.25 * f['6']

            f['11'+c] = withholding + inputs.get('estimated_payments',[0,0,0,0])[period]

            f['12'+c] = overpayment or None
            f['13'+c] = f['11'+c] + f['12'+c]
            f['14'+c] = underpayment or None
            f['15'+c] = max(0, f['13'+c] - f['14'+c])
            f['16'+c] = max(0, f['14'+c] - f['13'+c])
            if f['10'+c] >= f['15'+c]:
                f.must_file = True
                f.comment['17'+c] = 'Underpayment (Period %d)' % (period + 1)
                f['17'+c] = f['10'+c] - f['15'+c]
            else:
                f.comment['18'+c] = 'Overpayment (Period %d)' % (period + 1)
                f['18'+c] = f['15'+c] - f['10'+c]
            underpayment = f['16'+c] + f['17'+c]
            overpayment = f['18'+c]

        # TODO: penalty computation

    def title(self):
        return 'Form 2210'
