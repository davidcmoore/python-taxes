from form import Form, FilingStatus
from ca540 import CA540
from ca540sca import CA540sca
import math

class CA5805(Form):

    def __init__(f, inputs):
        super(CA5805, f).__init__(inputs)
        f.must_file = True
        f.addForm(f)

        cols = ['a.', 'b.', 'c.', 'd.']
        annualizer = [4.0, 2.4, 1.5, 1.0]
        percentages = [0.27, 0.63, 0.63, 0.90]
        regular_sched = [0.3, 0.4, 0.0, 0.3]

        f['1'] = inputs['current_tax']
        f['2'] = f['1'] * .9
        #f['3'] = inputs['withholding']
        #f['4'] = f['1'] - f['3']
        #if f['4'] < 500:
        #    return
        f['5'] = 1.1 * inputs['previous_tax']
        if inputs['agis'][3] >= 1000000:
            f['6'] = f['2']
        else:
            f['6'] = min(f['2'], f['5'])

        for i in range(0,4):
            c = cols[i]
            f[c+'1'] = inputs['agis'][i]
            f[c+'3'] = f[c+'1'] * annualizer[i]
            f[c+'7'] = CA540sca.STD_DED[inputs['status']]
            f[c+'8'] = f[c+'7']
            f[c+'9'] = max(0, f[c+'3'] - f[c+'8'])
            f.comment[c+'10'] = "Tax"
            f[c+'10'] = CA540.tax_rate_schedule(inputs['status'], f[c+'9'])
            f[c+'11'] = inputs['exemption_credits'][i]
            f[c+'12'] = f[c+'10'] - f[c+'11']
            f[c+'13'] = inputs['total_credits'][i]
            f[c+'14a'] = max(0, f[c+'12'] - f[c+'13'])
            f[c+'14e'] = f[c+'14a']
            f[c+'16'] = f[c+'14e'] * percentages[i]
            for j in range(0,i):
                f[c+'17'] = f[c+'17'] + f[cols[j]+'23']
            f.comment[c+'18'] = "Annualized installment"
            f[c+'18'] = max(0, f[c+'16'] - f[c+'17'])
            f[c+'19'] = f['6'] * regular_sched[i]
            if i > 0:
                f[c+'20'] = f[cols[i-1]+'22']
            f.comment[c+'21'] = "Regular installment"
            f[c+'21'] = f[c+'19'] + f[c+'20']
            f[c+'22'] = max(0, f[c+'21'] - f[c+'18'])
            f.comment[c+'23'] = "Minimum installment"
            f[c+'23'] = min(f[c+'18'], f[c+'21'])
            f.comment[c+'24'] = "Withholding"
            f[c+'24'] = inputs['withholding'][i]

    def title(f):
        return 'CA Form 5805'
