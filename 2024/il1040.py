
from form import Form, FilingStatus

class IL1040(Form):
    PERSONAL_EXEMPTION = 2750  # 2024 IL value (example)
    DEPENDENT_EXEMPTION = 2750
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
        from il1040m import IL1040M
        m = f.addForm(IL1040M(inputs, f))
        f.comment['3'] = 'Other additions (Schedule M, line A)'
        f['3'] = m['A']

        # Line 4: Total income (Lines 1 + 2 + 3)
        f.comment['4'] = 'Total income (Lines 1 + 2 + 3)'
        f['4'] = f['1'] + f['2'] + f['3']

        # Line 5: Social Security benefits and certain retirement income (Schedule M, line B)
        f.comment['5'] = 'Social Security benefits and certain retirement income (Schedule M, line B)'
        f['5'] = m['B']

        # Line 6: Other subtractions (Schedule M, line 2)
        f.comment['6'] = 'Other subtractions (Schedule M, line 2)'
        f['6'] = m['2']

        # Line 7: Illinois base income (Line 4 minus Lines 5 and 6)
        f.comment['7'] = 'Illinois base income (Line 4 minus Lines 5 and 6)'
        f['7'] = f['4'] - f['5'] - f['6']

        # Line 8: Exemptions (personal and dependent)
        if inputs['status'] in [FilingStatus.JOINT, FilingStatus.WIDOW]:
            personal = 2
        else:
            personal = 1
        f.comment['8'] = 'Exemptions (personal and dependent)'
        f['8'] = personal * f.PERSONAL_EXEMPTION + inputs.get('dependents', 0) * f.DEPENDENT_EXEMPTION

        # Line 9: Net income (Line 7 minus Line 8)
        f.comment['9'] = 'Net income (Line 7 minus Line 8)'
        f['9'] = max(0, f['7'] - f['8'])

        # Line 10: Tax (4.95% of Line 9)
        f.comment['10'] = 'Tax (4.95% of Line 9)'
        f['10'] = int(round(f['9'] * f.TAX_RATE))

        # Line 11: Tax after credits (apply ICR, CR, ED, 529)
        from il1040icr import IL1040ICR
        icr = f.addForm(IL1040ICR(inputs, f))
        from il1040cr import IL1040CR
        from il1040ed import IL1040ED
        from il1040529 import IL1040529
        cr = f.addForm(IL1040CR(inputs, f))
        ed = f.addForm(IL1040ED(inputs, f))
        s529 = f.addForm(IL1040529(inputs, f))
        total_credits = (icr['4'] or 0) + (cr['2'] or 0) + (ed['2'] or 0) + (s529['2'] or 0)
        f.comment['11'] = 'Tax after credits (Line 10 minus total credits)'
        f['11'] = max(0, f['10'] - total_credits)

        # Line 12: Payments (withholding, estimated, etc.)
        f.comment['12'] = 'Payments (withholding, estimated, etc.)'
        f['12'] = inputs.get('payments', 0)

        # Line 13: Refund or Amount Owed (Line 12 minus Line 11)
        f.comment['13'] = 'Refund or Amount Owed (Line 12 minus Line 11)'
        f['13'] = f['12'] - f['11']

        # Add interest/dividends and business income schedules
        from il1040in import IL1040IN
        from il1040bus import IL1040BUS
        from il1040use import IL1040USE
        in_sched = f.addForm(IL1040IN(inputs, f))
        bus_sched = f.addForm(IL1040BUS(inputs, f))
        use_sched = f.addForm(IL1040USE(inputs, f))
