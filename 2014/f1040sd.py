from form import Form, FilingStatus

class F1040sd(Form):
    def __init__(f, inputs):
        super(F1040sd, f).__init__(inputs)
        if 'capital_gain_long' not in inputs and 'capital_gain_short' not in inputs:
            return
        f.must_file = True
        f['1'] = inputs.get('capital_gain_short')
        f['7'] = f.rowsum(['1', '2', '3', '4', '5', '6'])
        f['8'] = inputs.get('capital_gain_long')
        f['13'] = inputs.get('capital_gain_dist')
        f['15'] = f.rowsum(['8', '9', '10', '11', '12', '13', '14'])
        f['16'] = f.rowsum(['7', '15'])
        if f['16'] < 0:
            cutoff = -3000
            if inputs['status'] == FilingStatus.SEPARATE:
                cutoff = -1500
            f['21'] = max(f['16'], cutoff)

        # If lines 15 and 16 are both gains and line 18 or 19 has a value:
        #   Use the Schedule D tax worksheet
        # Else if lines 15 and 16 are both gains or you have qualified divs:
        #   Use the Qualified Dividends and Capital Gain Tax Worksheet
        # Else
        #   Use tax tables

    def title(self):
        return 'Schedule D'
