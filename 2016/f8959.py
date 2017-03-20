from form import Form, FilingStatus

class F8959(Form):
    """Form 8959, Additional Medicare Tax"""
    THRESHOLDS = [200000, 250000, 125000, 200000, 200000]
    def __init__(f, inputs, f1040, sse):
        super(F8959, f).__init__(inputs)
        f['1'] = f.spouseSum(inputs, 'wages_medicare')
        # TODO: forms 4137, 8919
        f['4'] = f.rowsum(['1', '2', '3'])
        if f.get('4'):
            f['5'] = f.THRESHOLDS[inputs['status']]
            f['6'] = max(0, f['4'] - f['5'])
            f['7'] = f['6'] * .009

        if inputs['status'] == FilingStatus.JOINT:
            if sse[0].mustFile() or sse[1].mustFile():
                f['8'] = max(0, (sse[0]['A4'] or sse[0]['B6'] or 0) +
                                (sse[1]['A4'] or sse[1]['B6'] or 0))
        else:
            if sse.mustFile():
                f['8'] = max(0, sse['A4'] or sse['B6'])
        if f.get('8'):
            assert(f['8'] >= 400)
            f['9'] = f.THRESHOLDS[inputs['status']]
            f['10'] = f.get('4')
            f['11'] = max(0, f['9'] - f['10'])
            f['12'] = max(0, f['8'] - f['11'])
            f['13'] = f['12'] * .009 or None

        if f.get('14'):
            f['15'] = f.THRESHOLDS[inputs['status']]
            f['16'] = max(0, f['14'] - f['15'])
            f['17'] = f['16'] * .009 or None

        f['18'] = f.rowsum(['7', '13', '17'])

        f['19'] = f.spouseSum(inputs, 'medicare_withheld')
        f['20'] = f.get('1')
        f['21'] = f['20'] * .0145 or None
        if f['19'] or f['21']:
            f['22'] = max(0, f['19'] - f['21'])
        f['24'] = f.rowsum(['22', '23'])

        if f.get('18') or f.get('24'):
            f.must_file = True
        return

    def title(self):
        return 'Form 8959'
