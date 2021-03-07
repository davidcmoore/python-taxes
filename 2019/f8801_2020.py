from form import Form, FilingStatus

class F8801_2020(Form):
    """Form 8801, Credit for Prior Year Minimum Tax

    This form is for 2020, but since it depends on values
    from 2019, it is generated along with 2019's
    forms. Line 21 from this form must be manually entered into
    2020's input dictionary.
    """
    def __init__(f, inputs, f1040, f6251, f8801, sched_d):
        super(F8801_2020, f).__init__(inputs)
        f['1'] = f6251.rowsum(['1', '2e'])
        f['2'] = f6251.rowsum(['2a', '2b', '2c', '2d', '2g', '2h'])
        # TODO: Line 3, minimum tax credit net operating loss deduction
        f['4'] = max(0, f['1'] + f['2'] + f['3'])
        assert(inputs['status'] != FilingStatus.SEPARATE or f['4'] <= 718800)
        f.comment['15'] = 'Net minimum tax on exclusion items'
        if f['4'] == 0:
            f['15'] = 0
        else:
            f['5'] = f6251.EXEMPTIONS[inputs['status']]
            f['6'] = f6251.EXEMPT_LIMITS[inputs['status']]
            f['7'] = max(0, f['4'] - f['6'])
            f['8'] = f['7'] * 0.25
            f['9'] = max(0, f['5'] - f['8'])
            f['10'] = max(0, f['4'] - f['9'])
            if f['10'] == 0:
                f['15'] = 0
            else:
                # TODO: form 2555
                if (f1040['6'] and not sched_d.mustFile()) or f1040['3a'] or \
                        (sched_d['15'] > 0 and sched_d['16'] > 0):
                    f['27'] = f.get('10')
                    # TODO: Schedule D tax worksheet
                    assert(not sched_d['18'] and not sched_d['19'])
                    cg_worksheet = f1040.div_cap_gain_tax_worksheet(inputs,
                                                                    sched_d)
                    f['28'] = cg_worksheet['6']
                    f['30'] = f.get('28')
                    f['31'] = min(f['27'], f['30'])
                    f['32'] = f['27'] - f['31']
                    f['33'] = f6251.amt(inputs['status'], f['32'])
                    f['34'] = f1040.CAPGAIN15_LIMITS[inputs['status']]
                    f['35'] = cg_worksheet['7']
                    f['36'] = max(0, f['34'] - f['35'])
                    f['37'] = min(f['27'], f['28'])
                    f['38'] = min(f['36'], f['37'])
                    f['39'] = f['37'] - f['38']
                    f['40'] = f1040.CAPGAIN20_LIMITS[inputs['status']]
                    f['41'] = f.get('36')
                    f['42'] = cg_worksheet['7']
                    f['43'] = f.rowsum(['41', '42'])
                    f['44'] = max(0, f['40'] - f['43'])
                    f['45'] = min(f['39'], f['44'])
                    f['46'] = f['45'] * .15
                    f['47'] = f.rowsum(['38', '45'])
                    if f['47'] != f['27']:
                        f['48'] = f['37'] - f['47']
                        f['49'] = f['48'] * .20
                        if f['29']:
                            f['50'] = f.rowsum(['32', '47', '48'])
                            f['51'] = f['27'] - f['50']
                            f['52'] = f['51'] * .25
                    f['53'] = f.rowsum(['33', '46', '49', '52'])
                    f['54'] = f6251.amt(inputs['status'], f['27'])
                    f['55'] = min(f['53'], f['54'])
                    f['11'] = f['55']
                else:
                    f['11'] = f6251.amt(inputs['status'], f['10'])
                # TODO: Form 1116
                f['12'] = f1040.get('s3_1')
                f.comment['13'] = 'Tentative minimum tax on exclusion items'
                f['13'] = f['11'] - f['12']
                f['14'] = f6251.get('10')
                f.comment['15'] = 'Net minimum tax on exclusion items'
                f['15'] = max(0, f['13'] - f['14'])

        f['16'] = f6251.get('11')
        f['17'] = f.get('15')
        f['18'] = f['16'] - f['17']
        f.comment['19'] = '2019 credit carryforward'
        f['19'] = f8801.get('26')
        f.comment['21'] = 'Accum. credit (enter in 2020 inputs as \'prior_amt_credit\')'
        f['21'] = max(0, f['18'] + f['19'] + f['20'])
        if f['21']:
            f.must_file = True

    def title(self):
        return 'Form 8801 (for 2020 filing)'
