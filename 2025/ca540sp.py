from form import Form, FilingStatus

class CA540sp(Form):
    EXEMPTION_LIMITS = [347808, 463745, 231868, 347808, 463745]
    EXEMPTIONS = [92749, 123667, 61830, 92749, 123667]

    def __init__(f, inputs, ca540, ca540sca, f1040, f1040sa):
        super(CA540sp, f).__init__(inputs)
        if ca540['18'] != ca540sca.STD_DED[inputs['status']]:
            f['2'] = min(f1040sa['4'], .025 * f1040['11b'])
            f['3'] = f1040sa.rowsum(['5b', '5c'])
            f['5'] = ca540sca['2_25']
        else:
            f['1'] = ca540['18']
        f['14'] = f.rowsum(['[1-9]', '1[0-3]'])
        f['15'] = ca540['19']
        if not f['15']:
            f['15'] = ca540['17'] - ca540['18']
        f['16'] = ca540sca.rowsum(['1B_B9b1', '1B_B9b2', '1B_B9b3'])
        f['17'] = -max(0, f1040['s1_3'])
        if ca540['18'] != ca540sca.STD_DED[inputs['status']]:
            f['18'] = -(ca540sca['2_28'] - ca540sca['2_29']) or None
        f['19'] = f.rowsum(['1[4-8]'])
        f.comment['21'] = 'AMT Income'
        f['21'] = f['19'] - f['20']
        assert(inputs['status'] != FilingStatus.SEPARATE or f['21'] <= 479188)

        f.comment['22'] = 'Exemption Amount'
        f['22'] = f.exemption(inputs, f1040)
        f['23'] = max(0, f['21'] - f['22'])
        f.comment['24'] = 'Tentative Minimum Tax'
        f['24'] = f['23'] * .07
        f.comment['25'] = 'Regular Tax'
        f['25'] = ca540['31']
        f.comment['26'] = 'AMT'
        f['26'] = max(0, f['24'] - f['25'])
        if f['26'] or (f['21'] > f['22'] and f.rowsum(['4', '[7-9]', '1[0-3]'])):
            f.must_file = True

    def exemption(f, inputs, f1040):
        w = {}
        w['1'] = f.EXEMPTIONS[inputs['status']]
        w['2'] = f['21']
        w['3'] = f.EXEMPTION_LIMITS[inputs['status']]
        w['4'] = max(0, w['2'] - w['3'])
        w['5'] = w['4'] * .25
        w['6'] = max(0, w['1'] - w['5'])
        if inputs.get('can_be_dependent', False):
            w['7'] = 9750
            w['8'] = f1040.earned_income()
            w['9'] = w['7'] + w['8']
            w['10'] = min(w['6'], w['9'])
            return w['10']
        else:
            return w['6']

    def title(self):
        return 'CA 540 Schedule P'
