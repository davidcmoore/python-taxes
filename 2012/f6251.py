from form import Form, FilingStatus

class F6251(Form):
    EXEMPTIONS = [50600, 78750, 39375, 50600, 78750]
    EXEMPT_LIMITS = [112500, 150000, 75000, 112500, 150000]
    RATE_CHANGE = [175000, 175000, 87500, 175000, 175000]
    CAP_GAIN_LIMITS = [35350, 70700, 35350, 47350, 70700]
    def __init__(f, inputs, f1040, sched_a, sched_d):
        super(F6251, f).__init__(inputs)
        if sched_a:
            f['1'] = f1040.get('41')
            if sched_a['4']:
                f['2'] = min(sched_a['4'], f1040['38'] * .025)
            f['3'] = sched_a.get('9')
            f['5'] = sched_a.get('27')
        else:
            f['1'] = f1040.get('38')
        if '10' in f1040:
            f['7'] = -f1040['10']
        f['28'] = f.rowsum([str(i) for i in xrange(0,28)])
        if inputs['status'] == FilingStatus.SEPARATE:
            if f['28'] > 390000:
                f['28'] += 39375
            elif f['28'] > 232500:
                f['28'] += (f['28'] - 232500) * .25
        f['29'] = f.exemption(inputs)
        f['30'] = f['28'] - f['29']
        if f['30'] <= 0:
            return

        if (f1040['13'] and not sched_d.mustFile()) or f1040['9b'] or \
                (sched_d['15'] > 0 and sched_d['16'] > 0):
            f['36'] = f['30']
            # TODO: Schedule D tax worksheet
            assert(not sched_d['18'] and not sched_d['19'])
            cg_worksheet = f.cap_gain_worksheet(f1040, sched_d)
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
            f['49'] = f['48'] * .15
            if f['38']:
                f['50'] = f['40'] - f['46']
                f['51'] = f['50'] * .25
            f['52'] = f.rowsum(['42', '49', '51'])
            f['53'] = f.amt(inputs['status'], f['36'])
            f['54'] = min(f['52'], f['53'])
            f['31'] = f['54']
        else:
            f['31'] = f.amt(inputs['status'], f['30'])

        f['32'] = f1040['47']
        f['33'] = f['31'] - f['32']
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
        return w['6']

    def amt(f, status, val):
        thresh = f.RATE_CHANGE[status]
        if val <= thresh:
            return val * .26
        else:
            return val * .28 - thresh * .02

    def cap_gain_worksheet(f, f1040, sched_d):
        w = {}
        w['1'] = f1040['43']
        w['2'] = f1040['9b']
        if sched_d.mustFile():
            w['3'] = max(0, min(sched_d['15'], sched_d['16']))
        else:
            w['3'] = f1040['13']
        w['4'] = w['2'] + w['3']
        w['5'] = 0 # TODO: form 4952
        w['6'] = max(0, w['4'] - w['5'])
        w['7'] = max(0, w['1'] - w['6'])
        return w

    def title(self):
        return 'Form 6251'
