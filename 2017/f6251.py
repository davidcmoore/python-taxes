from form import Form, FilingStatus

class F6251(Form):
    """Form 6251, Alternative Minimum Tax"""
    EXEMPTIONS = [54300, 84500, 42250, 54300, 84500]
    EXEMPT_LIMITS = [120700, 160900, 80450, 120700, 160900]
    RATE_CHANGE = [187800, 187800, 93900, 187800, 187800]
    def __init__(f, inputs, f1040, sched_a, sched_d):
        super(F6251, f).__init__(inputs)
        if sched_a:
            f['1'] = f1040.get('41')
            f['3'] = sched_a.get('9')
            f['5'] = sched_a.get('27')
            sa_worksheet = sched_a.worksheet(inputs, f1040)
            if '9' in sa_worksheet:
                f['6'] = -sa_worksheet['9']
        else:
            f['1'] = f1040.get('38')
        if '10' in f1040:
            # TODO: refunds from 1040, line 21
            f['7'] = -f1040['10']

        if (f.rowsum([str(i) for i in xrange(8,28)]) or 0) < 0:
            f.must_file = True

        f['28'] = f.rowsum([str(i) for i in xrange(1,28)])
        if inputs['status'] == FilingStatus.SEPARATE:
            UPPER = 8 * EXEMPTIONS[inputs['status']] + \
                        EXEMPT_LIMITS[inputs['status']]
            LOWER = 4 * EXEMPTIONS[inputs['status']] + \
                        EXEMPT_LIMITS[inputs['status']]
            if f['28'] >= UPPER:
                f['28'] += EXEMPTIONS[inputs['status']]
            elif f['28'] > LOWER:
                f['28'] += (f['28'] - LOWER) * .25
        f['29'] = f.exemption(inputs)
        f['30'] = f['28'] - f['29']
        if f['30'] <= 0:
            # TODO: form 4972, schedule J
            f['30'] = 0
            f['34'] = f1040['44'] + f1040['46'] - f1040['48']
            return

        # TODO: capital gains refigured for the AMT
        # TODO: form 2555
        if (f1040['13'] and not sched_d.mustFile()) or f1040['9b'] or \
                (sched_d['15'] > 0 and sched_d['16'] > 0):
            f['36'] = f['30']
            # TODO: Schedule D tax worksheet
            assert(not sched_d['18'] and not sched_d['19'])
            cg_worksheet = f1040.div_cap_gain_tax_worksheet(inputs, sched_d)
            f['37'] = cg_worksheet['6']
            f['38'] = sched_d.get('19')
            f['39'] = f['37']
            f['40'] = min(f['36'], f['39'])
            f['41'] = f['36'] - f['40']
            f['42'] = f.amt(inputs['status'], f['41'])
            f['43'] = f1040.BRACKET_LIMITS[inputs['status']][1]
            f['44'] = cg_worksheet['7']
            f['45'] = max(0, f['43'] - f['44'])
            f['46'] = min(f['36'], f['37'])
            f['47'] = min(f['45'], f['46'])
            f['48'] = f['46'] - f['47']
            f['49'] = f1040.BRACKET_LIMITS[inputs['status']][5]
            f['50'] = f['45']
            f['51'] = cg_worksheet['7']
            f['52'] = f['50'] + f['51']
            f['53'] = max(0, f['49'] - f['52'])
            f['54'] = min(f['48'], f['53'])
            f['55'] = f['54'] * .15
            f['56'] = f['47'] + f['54']
            if f['56'] != f['36']:
                f['57'] = f['46'] - f['56']
                f['58'] = f['57'] * .20
                if f['38']:
                    f['59'] = f.rowsum(['41', '56', '57'])
                    f['60'] = f['36'] - f['59']
                    f['61'] = f['60'] * .25
            f['62'] = f.rowsum(['42', '55', '58', '61'])
            f['63'] = f.amt(inputs['status'], f['36'])
            f['64'] = min(f['62'], f['63'])
            f['31'] = f['64']
        else:
            f['31'] = f.amt(inputs['status'], f['30'])

        # TODO: form 1116
        f['32'] = f1040['48']
        f.comment['33'] = 'Tentative Minimum Tax'
        f['33'] = f['31'] - f['32']
        # TODO: form 4972, schedule J
        f.comment['34'] = 'Regular Tax'
        f['34'] = f1040['44'] + f1040['46'] - f1040['48']
        f.comment['35'] = 'AMT'
        f['35'] = max(0, f['33'] - f['34'])
        if f['31'] > f['34']:
            f.must_file = True

    def exemption(f, inputs):
        w = {}
        w['1'] = f.EXEMPTIONS[inputs['status']]
        w['2'] = f['28']
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
