from form import Form, FilingStatus

class CA540sca(Form):
    STD_DED = [4401, 8802, 4401, 8802, 8802]

    def __init__(f, inputs, f1040, f1040sa):
        super(CA540sca, f).__init__(inputs)
        f['B19'] = f1040.get('s19')
        f['B22'] = f.rowsum(['B1', 'B2b', 'B3b', 'B4b', 'B5b', 'B10', 'B12',
                             'B13', 'B14', 'B17', 'B18', 'B19', 'B21a', 'B21b',
                             'B21d', 'B21e', 'B21f'])
        f['C22'] = f.rowsum(['C1', 'C2b', 'C3b', 'C4b', 'C11', 'C12', 'C13',
                             'C14', 'C17', 'C18', 'C21c', 'C21f'])
        f['B36'] = f.rowsum(['B23', 'B24', 'B25'])
        f['C36'] = f.rowsum(['C24', 'C26', 'C31a', 'C33'])
        f['B37'] = f['B22'] - f['B36']
        f['C37'] = f['C22'] - f['C36']

        f['IIB5a'] = f1040sa['5a']
        f['IIB5e'] = f1040sa['5a']
        f['IIC5e'] = f1040sa['5d'] - f1040sa['5e']
        f['IIB7'] = f.rowsum(['IIB5e', 'IIB6'])
        f['IIC7'] = f['IIC5e']

        f['IIC8e'] = f.rowsum(['IIC8a', 'IIC8b', 'IIC8c'])
        f['IIB10'] = f['IIB9']
        f['IIC10'] = f.rowsum(['IIC8e', 'IIC9'])

        f['IIB14'] = f.rowsum(['IIB11', 'IIB12', 'IIB13'])
        f['IIC14'] = f.rowsum(['IIC11', 'IIC12', 'IIC13'])

        f['IIB17'] = f.rowsum(['IIB7', 'IIB10', 'IIB14', 'IIB15', 'IIB16'])
        f['IIC17'] = f.rowsum(['IIC7', 'IIC10', 'IIC14', 'IIC15', 'IIC16'])

        f['II18'] = f1040sa['17'] - f['IIB17'] + f['IIC17']

        f['II22'] = f.rowsum(['II19', 'II20', 'II21'])
        f['II23'] = f1040['7']
        f['II24'] = max(0, 0.02 * f['II23'])
        f['II25'] = max(0, f['II22'] - f['II24'])
        f['II26'] = f['II18'] + f['II25']
        f['II28'] = f['II26'] + f['II27']
        f['II29'] = f.itemized_deductions_worksheet(inputs, f1040, f1040sa)
        f['II30'] = max(f['II29'], f.STD_DED[inputs['status']])

        if f['B37'] or f['C37'] or f['II30'] != f.STD_DED[inputs['status']]:
            f.must_file = True

    def itemized_deductions_worksheet(f, inputs, f1040, f1040sa):
        LIMITS = [194504, 389013, 194504, 291760, 389013]
        w = {}
        w['1'] = f['II28']
        if f1040['7'] <= LIMITS[inputs['status']]:
            return w['1']
        w['2'] = f1040sa.rowsum(['4', '9', '15']) or 0
        w['3'] = w['1'] - w['2']
        if w['3'] == 0:
            return w['1']
        w['4'] = w['3'] * .8
        w['5'] = f1040['7']
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
