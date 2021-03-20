from form import Form, FilingStatus

class CA540sp(Form):
    EXEMPTION_LIMITS = [280424, 373899, 186946, 280424, 373899]
    EXEMPTIONS = [74780, 99707, 49851, 74780, 99707]

    def __init__(f, inputs, ca540, ca540sca, f1040, f1040sa):
        super(CA540sp, f).__init__(inputs)
        if ca540['18'] != ca540sca.STD_DED[inputs['status']]:
            f['2'] = min(f1040sa['4'], .025 * f1040['11'])
            f['3'] = f1040sa.rowsum(['5b', '5c'])
            f['5'] = ca540sca['2_25']
        else:
            f['1'] = ca540['18']
        f['14'] = f.rowsum(['1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
                            '11', '12', '13'])
        f['15'] = ca540['19']
        if not f['15']:
            f['15'] = ca540['17'] - ca540['18']
        f['16'] = ca540sca.rowsum(['1B_B8b', '1B_B8d', '1B_B8e'])
        f['17'] = -max(0, f1040['s1_3'])
        if ca540['18'] != ca540sca.STD_DED[inputs['status']]:
            f['18'] = -(ca540sca['2_28'] - ca540sca['2_29']) or None
        f['19'] = f.rowsum(['14', '15', '16', '17', '18'])
        f['21'] = f['19'] - f['20']
        assert(inputs['status'] != FilingStatus.SEPARATE or f['21'] <= 386350)

        f['22'] = f.exemption(inputs)
        f['23'] = max(0, f['21'] - f['22'])
        f['24'] = f['23'] * .07
        f['25'] = ca540['31']
        f['26'] = max(0, f['24'] - f['25'])
        if f['26'] or f['21'] > f['22'] and f.rowsum(['4', '7', '8', '9', '10',
                                                      '11', '12', '13']):
            f.must_file = True

    def exemption(f, inputs):
        w = {}
        w['1'] = f.EXEMPTIONS[inputs['status']]
        w['2'] = f['21']
        w['3'] = f.EXEMPTION_LIMITS[inputs['status']]
        w['4'] = max(0, w['2'] - w['3'])
        w['5'] = w['4'] * .25
        w['6'] = max(0, w['1'] - w['5'])
        return w['6']

    def title(self):
        return 'CA 540 Schedule P'
