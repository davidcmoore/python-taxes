from form import Form

class CA5805(Form):

    def __init__(f, inputs, ca540):
        super(CA5805, f).__init__(inputs)
        f.addForm(f)

        #cols = ['a.', 'b.', 'c.', 'd.']
        #annualizer = [4.0, 2.4, 1.5, 1.0]
        #percentages = [0.27, 0.63, 0.63, 0.90]
        regular_sched = [0.3, 0.4, 0.0, 0.3]

        f['1'] = ca540.rowsum(['48', '61', '62'])
        f.comment['1'] = 'Current year tax'
        f['2'] = f['1'] * .9
        f['3'] = ca540.rowsum(['71', '73'])
        f.comment['3'] = 'Withholding'
        f['4'] = f['1'] - f['3']
        if f['4'] < 500:
            return
        if 'state_safe_harbor_tax' in inputs and ca540['17'] < 1000000:
            f['5'] = inputs['state_safe_harbor_tax']
            f['6'] = min(f['2'], f['5'])
        else:
            f['6'] = f['2']
        f.comment['6'] = 'Required annual payment'

        if f['6'] <= f['3']:
            return

        overpayment = 0
        underpayment = 0
        for c in ['a', 'b', 'c', 'd']:
            period = ord(c) - ord('a')
            f['w1'+c] = regular_sched[period] * f['6']
            if 'state_withholding_by_period' in inputs:
                assert(abs(sum(inputs['state_withholding_by_period']) - inputs['state_withholding']) < 0.01)
                withholding = inputs['state_withholding_by_period'][period]
            else:
                withholding = regular_sched[period] * f['3']

            f['w2'+c] = withholding + inputs.get('state_estimated_payments',[0,0,0,0])[period]

            f['w3'+c] = overpayment
            f['w4'+c] = f['w2'+c] + f['w3'+c]
            f['w5'+c] = underpayment
            f['w6'+c] = max(0, f['w4'+c] - f['w5'+c])
            f['w7'+c] = max(0, f['w5'+c] - f['w4'+c])
            if f['w1'+c] >= f['w6'+c]:
                f.comment['w8'+c] = 'Underpayment (Period %d)' % (period + 1)
                f['w8'+c] = f['w1'+c] - f['w6'+c]
                f.must_file = True
            else:
                f.comment['w9'+c] = 'Overpayment (Period %d)' % (period + 1)
                f['w9'+c] = f['w6'+c] - f['w1'+c]
            underpayment = f['w7'+c] + f['w8'+c]
            overpayment = f['w9'+c]

        return
        # TODO: The rest of this form

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
            f[c+'14c'] = f[c+'14a']
            f[c+'16'] = f[c+'14c'] * percentages[i]
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
