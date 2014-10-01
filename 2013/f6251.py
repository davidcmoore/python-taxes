from form import Form, FilingStatus

class F6251(Form):
    """Form 6251, Alternative Minimum Tax"""
    EXEMPTIONS = [51900, 80800, 40400, 51900, 80800]
    EXEMPT_LIMITS = [115400, 153900, 76950, 115400, 153900]
    RATE_CHANGE = [179500, 179500, 89750, 179500, 179500]
    CAP_GAIN_LIMITS = [36250, 72500, 36250, 48600, 72500]
    def __init__(f, inputs, f1040, sched_a, sched_d):
        super(F6251, f).__init__(inputs)
        if sched_a:
            f['1'] = f1040.get('41')
            if sched_a['4']:
                f['2'] = min(sched_a['4'], f1040['38'] * .025)
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
        f['28'] = f.rowsum([str(i) for i in xrange(1,28)])
        if inputs['status'] == FilingStatus.SEPARATE:
            if f['28'] > 400150:
                f['28'] += 40400
            elif f['28'] > 238550:
                f['28'] += (f['28'] - 238550) * .25
        f['29'] = f.exemption(inputs)
        f['30'] = f['28'] - f['29']
        if f['30'] <= 0:
            # TODO: form 4972, schedule J
            f['34'] = f1040['44'] - f1040['47']
            f.must_file = True
            return

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
            f['43'] = f.CAP_GAIN_LIMITS[inputs['status']]
            f['44'] = cg_worksheet['7']
            f['45'] = max(0, f['43'] - f['44'])
            f['46'] = min(f['36'], f['37'])
            f['47'] = min(f['45'], f['46'])
            f['48'] = f['46'] - f['47']
            f['49'] = f.line49_worksheet(inputs, cg_worksheet)
            f['50'] = min(f['48'], f['49'])
            f['51'] = f['50'] * .15
            f['52'] = f['47'] + f['50']
            if f['52'] != f['36']:
                f['53'] = f['46'] - f['52']
                f['54'] = f['53'] * .20
                if f['38']:
                    f['55'] = f.rowsum(['41', '52', '53'])
                    f['56'] = f['36'] - f['55']
                    f['57'] = f['56'] * .25
            f['58'] = f.rowsum(['42', '51', '54', '57'])
            f['59'] = f.amt(inputs['status'], f['36'])
            f['60'] = min(f['58'], f['59'])
            f['31'] = f['60']
        else:
            f['31'] = f.amt(inputs['status'], f['30'])

        # TODO: form 1116
        f['32'] = f1040['47']
        f['33'] = f['31'] - f['32']
        # TODO: form 4972, schedule J
        f['34'] = f1040['44'] - f1040['47']
        if f['33'] > f['34']:
            f['35'] = f['33'] - f['34']
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

    def line49_worksheet(f, inputs, cg_worksheet):
        LIMITS = [400000, 450000, 225000, 425000, 450000]
        w = {}
        w['1'] = LIMITS[inputs['status']]
        w['2'] = f['45']
        # TODO: schedule D tax worksheet
        w['3'] = cg_worksheet['7']
        w['4'] = w['2'] + w['3']
        w['5'] = max(0, w['1'] - w['4'])
        return w['5']

    def title(self):
        return 'Form 6251'
