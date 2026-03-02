from form import Form, FilingStatus

class F8995A(Form):
    """Form 8995A, Qualified Business Income Deduction"""
    def __init__(f, inputs, f1040, sched_d):
        super(F8995A, f).__init__(inputs)

        income = f1040['11a'] - f1040['s1a_13'] - f1040['12e']
        threshold = f1040.BRACKET_LIMITS[inputs['status']][3]
        phase_in = 100000 if inputs['status'] == FilingStatus.JOINT else 50000

        assert income >= threshold

        # TODO: SSTB or multiple businesses
        qbi  = f1040['s1_3'] - (f1040.rowsum(['s1_1[567]']) or 0) \
               + inputs.get('additional_qbi', 0)
        if qbi < 0 or inputs.get('qbi_carryforward'):
            # Schedule C
            f['sc_1a'] = qbi
            f['sc_2'] = inputs.get('qbi_carryforward')
            f['sc_3'] = f['sc_2'] + min(f['sc_1a'], 0)
            f['sc_4'] = max(0, f['sc_1a'])
            f['sc_5'] = max(-f['sc_4'], f['sc_3'])

            f['sc_1b'] = f.get('sc_5')
            f['sc_1c'] = max(0, f['sc_1a'] + f['sc_1b'])

            f.comment['sc_6'] = 'QBI carryforward'
            f['sc_6'] = min(f['sc_3'] - f['sc_5'], 0)
            f['2'] = f['sc_1c']
        else:
            f['2'] = qbi or None

        f['3'] = f['2'] * .20 or None
        f['5'] = f['4'] * .50 or None
        f['6'] = f['4'] * .25 or None
        f['8'] = f['7'] * .025 or None
        f['9'] = f.rowsum(['6', '8'])
        f['10'] = max(f['5'], f['9']) or None
        f['11'] = min(f['3'], f['10']) or None

        if income < (threshold + phase_in) and f['10'] < f['3']:
            f['17'] = f['3']
            f['18'] = f['10']
            f['19'] = f['17'] - f['18']
            f['20'] = income
            f['21'] = threshold
            f['22'] = f['20'] - f['21']
            f['23'] = phase_in
            f['24'] = f['22'] / f['23'] * 100
            f['25'] = f['19'] * f['24'] / 100
            f['26'] = f['17'] - f['25']

        f['12'] = f.get('26')
        f['13'] = max(f['11'], f['12']) or None
        f['15'] = (f['13'] - f['14']) or None
        f['16'] = f.get('15')

        f['27'] = f.get('16')
        f['28'] = inputs.get('section_199A_dividends')
        f['30'] = max(0, f['28'] + f['29']) or None
        f['31'] = f['30'] * 0.20 or None
        f['32'] = f.rowsum(['27', '31'])
        f['33'] = income

        if sched_d.mustFile():
            f['34'] = f1040['3a'] + max(0, min(sched_d['15'], sched_d['16']))
        else:
            f['34'] = f1040['3a'] + f1040['7a']

        f['35'] = max(0, f['33'] - f['34'])
        f['36'] = f['35'] * 0.20
        f['37'] = min(f['32'], f['36'])
        f.comment['39'] = 'Total QBI deduction'
        f['39'] = f.rowsum(['37', '38'])
        f.comment['40'] = 'REIT and PTP carryforward'
        f['40'] = min(0, f['28'] + f['29']) or None

        if f['39'] or f['40'] or f['sc_6'] or inputs.get('qbi_carryforward'):
            f.must_file = True

    def title(self):
        return 'Form 8995A'
