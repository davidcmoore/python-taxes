from form import Form, FilingStatus

class CA540sca(Form):
    STD_DED = [4803, 9606, 4803, 9606, 9606]

    def __init__(f, inputs, f1040, f1040sa):
        super(CA540sca, f).__init__(inputs)
        f['1A_B6b'] = f1040.get('6b')
        f['1B_B7'] = f1040.get('s1_7')
        f['1B_B9a'] = f.rowsum(['1B_B8b', '1B_B8e', '1B_B8m', '1B_B8n',
                                '1B_B8z'])
        f['1B_C9a'] = f.rowsum(['1B_C8a', '1B_C8c', '1B_C8d', '1B_C8o',
                                '1B_C8z'])
        f['1B_B10'] = f.rowsum(['1A_B1', '1A_B2b', '1A_B3b', '1A_B4b', '1A_B5b',
                                '1A_B6b', '1A_B7', '1B_B1', '1B_B3', '1B_B4',
                                '1B_B5', '1B_B6', '1B_B7', '1B_B9a', '1B_B9b1',
                                '1B_B9b2', '1B_B9b3', '1B_B9b4'])
        f['1B_C10'] = f.rowsum(['1A_C1', '1A_C2b', '1A_C3b', '1A_C4b', '1A_C5b',
                                '1A_C7', '1B_C2a', '1B_C3', '1B_C4', '1B_C5',
                                '1B_C6', '1B_C9a'])

        f['1C_B26'] = f.rowsum(['1C_B11', '1C_B12', '1C_B13', '1C_B15',
                                '1C_B17', '1C_B20', '1C_B25'])
        f['1C_C26'] = f.rowsum(['1C_C12', '1C_C14', '1C_C19a', '1C_C20',
                                '1C_C21', '1C_C25'])
        f['1C_B27'] = f['1B_B10'] - f['1C_B26']
        f['1C_C27'] = f['1B_C10'] - f['1C_C26']

        f['2_B5a'] = f1040sa['5a']
        f['2_B5e'] = f1040sa['5a']
        f['2_C5e'] = f1040sa['5d'] - f1040sa['5e']
        f['2_B7'] = f.rowsum(['2_B5e', '2_B6'])
        f['2_C7'] = f.rowsum(['2_C5e', '2_C6'])

        f['2_B8e'] = f.get('2_B8d')
        f['2_C8e'] = f.rowsum(['2_C8a', '2_C8b', '2_C8c'])
        f['2_B10'] = f.rowsum(['2_B8e', '2_B9'])
        f['2_C10'] = f.rowsum(['2_C8e', '2_C9'])

        f['2_B14'] = f.rowsum(['2_B11', '2_B12', '2_B13'])
        f['2_C14'] = f.rowsum(['2_C11', '2_C12', '2_C13'])

        f['2_B17'] = f.rowsum(['2_B7', '2_B10', '2_B14', '2_B15', '2_B16'])
        f['2_C17'] = f.rowsum(['2_C4', '2_C7', '2_C10', '2_C14', '2_C15',
                               '2_C16'])

        f['2_18'] = f1040sa['17'] - f['2_B17'] + f['2_C17']

        f['2_22'] = f.rowsum(['2_19', '2_20', '2_21'])
        f['2_23'] = f1040['11']
        f['2_24'] = max(0, 0.02 * f['2_23'])
        f['2_25'] = max(0, f['2_22'] - f['2_24'])
        f['2_26'] = f['2_18'] + f['2_25']
        f['2_28'] = f['2_26'] + f['2_27']
        f['2_29'] = f.itemized_deductions_worksheet(inputs, f1040, f1040sa)
        f['2_30'] = max(f['2_29'], f.STD_DED[inputs['status']])

        if f['1C_B27'] or f['1C_C27'] or \
           f['2_30'] != f.STD_DED[inputs['status']]:
            f.must_file = True

    def itemized_deductions_worksheet(f, inputs, f1040, f1040sa):
        LIMITS = [212288, 424581, 212288, 318437, 424581]
        w = {}
        w['1'] = f['2_28']
        if f1040['11'] <= LIMITS[inputs['status']]:
            return w['1']
        w['2'] = f1040sa.rowsum(['4', '9', '15']) or 0
        w['3'] = w['1'] - w['2']
        if w['3'] == 0:
            return w['1']
        w['4'] = w['3'] * .8
        w['5'] = f1040['11']
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
