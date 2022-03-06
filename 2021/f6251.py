from form import Form, FilingStatus

class F6251(Form):
    """Form 6251, Alternative Minimum Tax"""
    EXEMPTIONS = [73600, 114600, 57300, 73600, 114600]
    EXEMPT_LIMITS = [523600, 1047200, 523600, 523600, 1047200]
    RATE_CHANGE = [199900, 199900, 99950, 199900, 199900]
    def __init__(f, inputs, f1040, sched_a, sched_d, sched_d_re):
        """sched_d is the regular tax schedule D. sched_d_re is schedule D
           refigured for AMT.
        """
        super(F6251, f).__init__(inputs)
        f['1'] = f1040.get('15')
        if f['1'] == 0:
            f['1'] = f1040['11'] - f1040['14']
        f['2a'] = sched_a.get('7') if sched_a else f1040.get('12a')

        if 's1_1' in f1040:
            # TODO: refunds from 1040 schedule 1, line 8z
            f['2b'] = -f1040['s1_1']

        if (f.rowsum(['2' + chr(x) for x in range(ord('c'), ord('u'))] + \
                     ['3']) or 0) < 0:
            f.must_file = True

        f['4'] = f.rowsum(['2' + chr(x) for x in range(ord('a'), ord('u'))] + \
                           ['1', '3'])
        if inputs['status'] == FilingStatus.SEPARATE:
            UPPER = 8 * EXEMPTIONS[inputs['status']] + \
                        EXEMPT_LIMITS[inputs['status']]
            LOWER = 4 * EXEMPTIONS[inputs['status']] + \
                        EXEMPT_LIMITS[inputs['status']]
            if f['4'] >= UPPER:
                f['4'] += EXEMPTIONS[inputs['status']]
            elif f['4'] > LOWER:
                f['4'] += (f['4'] - LOWER) * .25
        f['5'] = f.exemption(inputs)
        f['6'] = f['4'] - f['5']
        if f['6'] <= 0:
            # TODO: form 4972, schedule J
            f['6'] = 0
            f['10'] = f1040['16'] + f1040['s2_2'] - f1040['s3_1']
            return

        # TODO: capital gains refigured for the AMT
        # TODO: form 2555
        if (f1040['7'] and not sched_d.mustFile()) or f1040['3a'] or \
                (sched_d_re['15'] > 0 and sched_d_re['16'] > 0):
            f['12'] = f['6']
            # TODO: Schedule D tax worksheet
            assert(not sched_d_re['18'] and not sched_d_re['19'])
            cg_re = f1040.div_cap_gain_tax_worksheet(inputs, sched_d_re)
            f['13'] = cg_re['4']
            f['14'] = sched_d_re.get('19')
            f['15'] = f['13']
            f['16'] = min(f['12'], f['15'])
            f['17'] = f['12'] - f['16']
            f['18'] = f.amt(inputs['status'], f['17'])
            f['19'] = f1040.CAPGAIN15_LIMITS[inputs['status']]
            cg = f1040.div_cap_gain_tax_worksheet(inputs, sched_d)
            f['20'] = cg['5']
            f['21'] = max(0, f['19'] - f['20'])
            f['22'] = min(f['12'], f['13'])
            f['23'] = min(f['21'], f['22'])
            f['24'] = f['22'] - f['23']
            f['25'] = f1040.CAPGAIN20_LIMITS[inputs['status']]
            f['26'] = f['21']
            f['27'] = cg['5']
            f['28'] = f['26'] + f['27']
            f['29'] = max(0, f['25'] - f['28'])
            f['30'] = min(f['24'], f['29'])
            f['31'] = f['30'] * .15
            f['32'] = f['23'] + f['30']
            if f['32'] != f['12']:
                f['33'] = f['22'] - f['32']
                f['34'] = f['33'] * .20
                if f['14']:
                    f['35'] = f.rowsum(['17', '32', '33'])
                    f['36'] = f['12'] - f['35']
                    f['37'] = f['36'] * .25
            f['38'] = f.rowsum(['18', '31', '34', '37'])
            f['39'] = f.amt(inputs['status'], f['12'])
            f['40'] = min(f['38'], f['39'])
            f['7'] = f['40']
        else:
            f['7'] = f.amt(inputs['status'], f['6'])

        # TODO: form 1116
        f['8'] = f1040['s3_1']
        f.comment['9'] = 'Tentative Minimum Tax'
        f['9'] = f['7'] - f['8']
        # TODO: form 4972, schedule J
        f.comment['10'] = 'Regular Tax'
        f['10'] = f1040['16'] + f1040['s2_2'] - f1040['s3_1']
        f.comment['11'] = 'AMT'
        f['11'] = max(0, f['9'] - f['10'])
        if f['7'] > f['10']:
            f.must_file = True

    def exemption(f, inputs):
        w = {}
        w['1'] = f.EXEMPTIONS[inputs['status']]
        w['2'] = f['4']
        w['3'] = f.EXEMPT_LIMITS[inputs['status']]
        w['4'] = max(w['2'] - w['3'], 0)
        w['5'] = w['4'] * .25
        w['6'] = max(w['1'] - w['5'], 0)
        # TODO: certain children under age 24
        return w['6']

    def amt(f, status, val):
        thresh = f.RATE_CHANGE[status]
        if val <= thresh:
            return val * .26
        else:
            return val * .28 - thresh * .02

    def title(self):
        return 'Form 6251'
