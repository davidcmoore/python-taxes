from form import Form, FilingStatus

class F2441(Form):
    """Form 2441, Child and Dependent Care Expenses"""
    def __init__(f, inputs, sse):
        super(F2441, f).__init__(inputs)
        # Part III must be completed before Part II
        f['15'] = f['12'] + f['13'] - f['14']
        f['17'] = min(f['15'], f['16'])

        # TODO: logic for filing separately
        assert(inputs['status'] != FilingStatus.SEPARATE)
        if inputs['status'] == FilingStatus.JOINT:
            f['18'] = f.earned_income(inputs['wages'][0], sse[0])
            f['19'] = f.earned_income(inputs['wages'][1], sse[1])
        else:
            f['18'] = f['19'] = f.earned_income(inputs['wages'], sse)
        f['20'] = min(f['17'], f['18'], f['19'])
        f['21'] = 5000
        # TODO: partnership/proprietorship-provided childcare benefits
        f['22'] = 0
        f['23'] = f['15'] - f['22']
        f['24'] = min(f['20'], f['21'], f['22'])
        f['25'] = min(f['20'], f['21'])
        f['26'] = max(0, f['23'] - f['25'])
        assert(f['24'] == 0)
        if f['24'] or f['25'] or f['26']:
            f.must_file = True
        f['27'] = min(inputs.get('dependent_care_persons', 0), 2) * 3000
        f['28'] = f['24'] + f['25']
        f['29'] = f['27'] - f['28']
        # TODO: child care credit
        assert(f['29'] <= 0)
        return

    def earned_income(f, wages, sse):
        if sse.mustFile():
            return wages + (sse['A3'] or sse['B3']) - (sse['A6'] or sse['B13'])
        else:
            return wages

    def title(self):
        return 'Form 2441'
