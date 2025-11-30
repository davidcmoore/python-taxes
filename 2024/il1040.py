
from form import Form, FilingStatus
from il1040m import IL1040M
from il1040e_eitc import IL1040E_EITC
from il1040icr import IL1040ICR

class IL1040(Form):
    PERSONAL_EXEMPTION = 2775  # 2024 IL value (example)
    DEPENDENT_EXEMPTION = 2775
    AGE_BLIND = 1000
    TAX_RATE = 0.0495  # 2024 IL flat rate

    def __init__(f, inputs, f1040):
        super(IL1040, f).__init__(inputs)
        f.must_file = True
        f.addForm(f)

        # Line 1: Federal Adjusted Gross Income (AGI)
        f.comment['1'] = 'Federal Adjusted Gross Income (AGI)'
        f['1'] = f1040['11']

        # Line 2: Federally tax-exempt interest and dividends
        f.comment['2'] = 'Federally tax-exempt interest and dividends'
        f['2'] = inputs.get('tax_exempt_interest', 0) + inputs.get('tax_exempt_dividends', 0)

        # Line 3: Other additions (Schedule M, line A)
        m = f.addForm(IL1040M(inputs, f))
        f.comment['3'] = 'Other additions (Schedule M, line A)'
        f['3'] = m['12']

        # Line 4: Total income
        f.comment['4'] = 'Total income'
        f['4'] = f.rowsum(['1', '2', '3'])

        f['7'] = m['42']
        f.comment['8'] = 'Total Subtractions to IL income'
        f['8'] = f.rowsum(['5' , '6', '7'])

        f.comment['9'] = 'Illinois Base Income'
        f['9'] = max(0, f['4'] - f['8'])

        lineC = inputs.get('C', 0)
        if inputs['status'] == FilingStatus.JOINT:
            if lineC == 0 or f['9'] <= lineC*2775:
                f['10a'] = 2 * f.PERSONAL_EXEMPTION
            elif lineC == 1 and f['9'] > 2775:
                f['10a'] = f.PERSONAL_EXEMPTION
            else:
                f['10a'] = 0
        else:
            if lineC == 0 or f['9'] <= 2775:
                f['10a'] = f.PERSONAL_EXEMPTION
            else:
                f['10a'] = 0

        f['10bc'] = inputs.get('age_blind_boxes', 0)*f.AGE_BLIND

        # Line 10d: Earned Income Credit (Schedule IL-E/EITC)
        e_eitc = f.addForm(IL1040E_EITC(inputs, f))
        f.comment['10d'] = 'Earned Income Credit (Schedule IL-E/EITC)'
        f['10d'] = e_eitc['1']

        f['10'] = 0.
        if inputs['status'] == FilingStatus.JOINT and f1040['11'] < 500000 or \
           f1040['11'] < 250000:
            f['10'] = f.rowsum(['10a', '10bc', '10d'])

        f.comment['11'] = 'IL net income'
        # TODO schedule NR for part-year/non-resident adjustments
        f['11'] = max(0, f['9'] - f['10'])
        f['12'] = int(round(f['11'] * f.TAX_RATE))

        # TODO line 13 schedule 4255

        f.comment['14'] = 'IL Income Tax'
        f['14'] = f.rowsum(['12', '13'])

        # TODO line 15 schedule CR

        icr = f.addForm(IL1040ICR(inputs, f))
        f['16'] = icr['13']

        # TODO line 17 schedule 1299-C

        f['18'] = f.rowsum(['15', '16', '17'])
        assert f['18'] < f['14'], "Total credits exceed tax!"

        f['19'] = f['14'] - f['18']
        # TODO line 20

        f['21'] = 0. # I already pay for all the use tax

        f['23'] = f.rowsum(['19', '20', '21', '22'])
        f['24'] = f['23']

        # f['25'] and f['26'] are inputs
        # I don't have K-1-T or K-1-P income/tax

        f['29'] = e_eitc.get('9') or 0
        f['30'] = e_eitc.get('12') or 0
        f.comment['31'] = 'Total payments and refundable credit'
        f['31'] = f.rowsum(['25', '26', '27', '28', '29', '30'])

        if f['31'] >= f['24']:
            f.comment['32'] = 'Refund (Line 31 minus Line 24)'
            f['32'] = f['31'] - f['24']
            f['33'] = 0
        else:
            f['32'] = 0
            f.comment['33'] = 'Amount owed (Line 24 minus Line 31)'
            f['33'] = f['24'] - f['31']


        # # Line 5: Social Security benefits and certain retirement income (Schedule M, line B)
        # f.comment['5'] = 'Social Security benefits and certain retirement income (Schedule M, line B)'
        # f['5'] = m['B']

        # # Line 6: Other subtractions (Schedule M, line 2)
        # f.comment['6'] = 'Other subtractions (Schedule M, line 2)'
        # f['6'] = m['2']

        # # Line 7: Illinois base income (Line 4 minus Lines 5 and 6)
        # f.comment['7'] = 'Illinois base income (Line 4 minus Lines 5 and 6)'
        # f['7'] = f['4'] - f['5'] - f['6']

        # # Line 8: Exemptions (personal and dependent)
        # if inputs['status'] in [FilingStatus.JOINT, FilingStatus.WIDOW]:
        #     personal = 2
        # else:
        #     personal = 1
        # f.comment['8'] = 'Exemptions (personal and dependent)'
        # f['8'] = personal * f.PERSONAL_EXEMPTION + inputs.get('dependents', 0) * f.DEPENDENT_EXEMPTION

        # # Line 9: Net income (Line 7 minus Line 8)
        # f.comment['9'] = 'Net income (Line 7 minus Line 8)'
        # f['9'] = max(0, f['7'] - f['8'])

        # # Line 10: Tax (4.95% of Line 9)
        # f.comment['10'] = 'Tax (4.95% of Line 9)'
        # f['10'] = int(round(f['9'] * f.TAX_RATE))

        # # Line 11: Tax after credits (apply ICR, CR, ED, 529)
        # from il1040icr import IL1040ICR
        # icr = f.addForm(IL1040ICR(inputs, f))
        # from il1040cr import IL1040CR
        # from il1040ed import IL1040ED
        # from il1040529 import IL1040529
        # cr = f.addForm(IL1040CR(inputs, f))
        # ed = f.addForm(IL1040ED(inputs, f))
        # s529 = f.addForm(IL1040529(inputs, f))
        # total_credits = (icr['4'] or 0) + (cr['2'] or 0) + (ed['2'] or 0) + (s529['2'] or 0)
        # f.comment['11'] = 'Tax after credits (Line 10 minus total credits)'
        # f['11'] = max(0, f['10'] - total_credits)

        # # Line 12: Payments (withholding, estimated, etc.)
        # f.comment['12'] = 'Payments (withholding, estimated, etc.)'
        # f['12'] = inputs.get('payments', 0)

        # # Line 13: Refund or Amount Owed (Line 12 minus Line 11)
        # f.comment['13'] = 'Refund or Amount Owed (Line 12 minus Line 11)'
        # f['13'] = f['12'] - f['11']

        # # Add interest/dividends and business income schedules
        # from il1040in import IL1040IN
        # from il1040bus import IL1040BUS
        # from il1040use import IL1040USE
        # in_sched = f.addForm(IL1040IN(inputs, f))


        # bus_sched = f.addForm(IL1040BUS(inputs, f))
        # use_sched = f.addForm(IL1040USE(inputs, f))

    def title(f):
        return 'Form IL-1040'