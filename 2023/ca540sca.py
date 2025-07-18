from form import Form, FilingStatus

class CA540sca(Form):
    STD_DED = [5363, 10726, 5363, 10726, 10726]

    def __init__(f, inputs, f1040, f1040sa):
        super(CA540sca, f).__init__(inputs)
        f['1A_B6b'] = f1040.get('6b')
        f['1A_B1z'] = f.rowsum(['1A_B1[a-i]'])
        f['1A_C1z'] = f.rowsum(['1A_C1[a-i]'])
        f['1B_B1'] = f1040.get('s1_1')
        f['1B_B7'] = f1040.get('s1_7')
        f['1B_B9a'] = f.rowsum(['1B_B8[a-z]'])
        f['1B_C9a'] = f.rowsum(['1B_C8[a-z]'])
        f['1B_B10'] = f.rowsum(['1(A_B(1z|[2-7][a-z]*)|B_B([1-7][a-z]*|9a|9b[1-3]))'])
        f['1B_C10'] = f.rowsum(['1(A_C(1z|[2-7][a-z]*)|B_C([1-7][a-z]*|9a))'])

        f['1C_B11'] = f1040.get('s1_11')
        f['1C_B13'] = f1040.get('s1_13')
        f['1C_B25'] = f.rowsum(['1C_B24[a-z]'])
        f['1C_C25'] = f.rowsum(['1C_C24[a-z]'])
        f['1C_B26'] = f.rowsum(['1C_B1[1-8]', '1C_B20', '1C_B25'])
        f['1C_C26'] = f.rowsum(['1C_C1[1-8]', '1C_C19a', '1C_C2[0-1]', '1C_C25'])
        f['1C_B27'] = f['1B_B10'] - f['1C_B26']
        f['1C_C27'] = f['1B_C10'] - f['1C_C26']

        f['2_B5a'] = f1040sa['5a']
        f['2_B5e'] = f1040sa['5a']
        f['2_C5e'] = f1040sa['5d'] - f1040sa['5e']
        f['2_B7'] = f.rowsum(['2_B5e', '2_B6'])
        f['2_C7'] = f.rowsum(['2_C5e', '2_C6'])

        f['2_C8e'] = f.rowsum(['2_C8[a-c]'])
        f['2_B10'] = f.rowsum(['2_B8e', '2_B9'])
        f['2_C10'] = f.rowsum(['2_C8e', '2_C9'])

        f['2_B14'] = f.rowsum(['2_B1[1-3]'])
        f['2_C14'] = f.rowsum(['2_C1[1-3]'])

        f['2_B17'] = f.rowsum(['2_B7', '2_B10', '2_B1[4-6]'])
        f['2_C17'] = f.rowsum(['2_C4', '2_C7', '2_C10', '2_C1[4-6]'])

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
        LIMITS = [237035, 474075, 237035, 355558, 474075]
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
