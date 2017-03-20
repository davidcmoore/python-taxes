from form import Form, FilingStatus

class CA540sca(Form):
    STD_DED = [4129, 8258, 4129, 8258, 8258]

    def __init__(f, inputs, f1040, f1040sa):
        super(CA540sca, f).__init__(inputs)
        f['B19'] = f1040.get('19')
        f['B22'] = f.rowsum(['B7', 'B8a', 'B9a', 'B10', 'B11', 'B12', 'B13',
                             'B14', 'B15b', 'B16b', 'B17', 'B18', 'B19',
                             'B20b', 'B21'])
        f['C22'] = f.rowsum(['C7', 'C8a', 'C9a', 'C10', 'C11', 'C12', 'C13',
                             'C14', 'C15b', 'C16b', 'C17', 'C18', 'C19',
                             'C20b', 'C21'])
        f['B36'] = f.rowsum(['B23', 'B24', 'B25', 'B34', 'B35'])
        f['C36'] = f.rowsum(['C24', 'C31a', 'C33'])
        f['B37'] = f['B22'] - f['B36']
        f['C37'] = f['C22'] - f['C36']

        f['38'] = f1040sa.rowsum(['4', '9', '15', '19', '20', '27', '28'])
        f['39'] = f1040sa.rowsum(['5', '8'])
        f['40'] = f['38'] - f['39']
        f['42'] = f.rowsum(['40', '41'])
        f['43'] = f.itemized_deductions_worksheet(inputs, f1040, f1040sa)
        f['44'] = max(f['43'], f.STD_DED[inputs['status']])
        if f['B37'] or f['C37'] or f['44'] != f.STD_DED[inputs['status']]:
            f.must_file = True

    def itemized_deductions_worksheet(f, inputs, f1040, f1040sa):
        LIMITS = [182459, 364923, 182459, 273692, 364923]
        w = {}
        w['1'] = f['42']
        if f1040['37'] <= LIMITS[inputs['status']]:
            return w['1']
        w['2'] = f1040sa.rowsum(['4', '14', '20']) or 0
        w['3'] = w['1'] - w['2']
        if w['3'] == 0:
            return w['1']
        w['4'] = w['3'] * .8
        w['5'] = f1040['37']
        w['6'] = LIMITS[inputs['status']]
        w['7'] = w['5'] - w['6']
        if w['7'] <= 0:
            return w['1']
        w['8'] = w['7'] * .06
        w['9'] = min(w['4'], w['8'])
        w['10'] = w['1'] - w['9']
        return w['10']

    def title(self):
        return 'CA 540 Schedule CA'
