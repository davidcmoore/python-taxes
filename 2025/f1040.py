from form import Form, FilingStatus
from f1040sse import F1040sse
from f1040sa import F1040sa
from f1040sd import F1040sd
from f1116 import F1116
from f2210 import F2210
from f2441 import F2441
from f6251 import F6251
from f8606 import F8606
from f8801 import F8801
#from f8801_2026 import F8801_2026
from f8812 import F8812
from f8889 import F8889
from f8959 import F8959
from f8960 import F8960
from f8995 import F8995
from f8995a import F8995A
import copy
import math
import pprint

# Inputs:
#   status (required)     - One of FilingStatus
#   exemptions (required) - A number
#   wages (optional)      - in dollars
#   wages_ss (optional)   - social security portion of wages
#   taxable_interest (optional)
#   tax_exempt_interest (optional)

class F1040(Form):
    STD_DED = [15750, 31500, 15750, 23625, 31500]
    AGE_BLIND = [2000, 1600, 1600, 2000, 1600]
    BRACKET_RATES = [0.10, 0.12, 0.22, 0.24, 0.32, 0.35, 0.37]
    BRACKET_LIMITS = [
        [11925, 48475, 103350, 197300, 250525, 626350], # SINGLE
        [23850, 96950, 206700, 394600, 501050, 751600], # JOINT
        [11925, 48475, 103350, 197300, 250525, 375800], # SEPARATE
        [17000, 64850, 103350, 197300, 250500, 626350], # HEAD
        [23850, 96950, 206700, 394600, 501050, 751600], # WIDOW
    ]
    CAPGAIN15_LIMITS = [48350, 96700, 48350, 64750, 96700]
    CAPGAIN20_LIMITS = [533400, 600050, 300000, 566700, 600050]
    SS_MAX = 10918.20

    def __init__(f, inputs={}):
        super(F1040, f).__init__(inputs)

        f.must_file = True
        f.addForm(f)
        if inputs['status'] == FilingStatus.JOINT:
            sse = []
            for i in [0,1]:
                inputs2 = copy.copy(inputs)
                for j in ['wages', 'wages_ss', 'business_income', 'business_expenses']:
                    if j in inputs:
                        inputs2[j] = inputs[j][i]
                x = F1040sse(inputs2)
                f.addForm(x)
                sse.append(x)
        else:
            sse = F1040sse(inputs)
            f.addForm(sse)

        f2441 = F2441(inputs, sse)
        f.addForm(f2441)

        f.comment['1a'] = 'Wages'
        f['1a'] = f.spouseSum(inputs, 'wages')
        f['1e'] = f2441.get('26')
        f['1z'] = f.rowsum(['1[a-h]'])
        f.comment['2a'] = 'Tax-exempt Interest'
        f['2a'] = inputs.get('tax_exempt_interest')
        f.comment['2b'] = 'Taxable Interest'
        f['2b'] = inputs.get('taxable_interest')
        f.comment['3a'] = 'Qualified Dividends'
        f['3a'] = inputs.get('qualified_dividends')
        f.comment['3b'] = 'Dividends'
        f['3b'] = inputs.get('dividends')

        f.comment['4b'] = 'Taxable IRA distributions'
        if 'F8606' in inputs:
            if inputs['status'] == FilingStatus.JOINT:
                f8606 = [f.addForm(F8606(inputs, 0)),
                         f.addForm(F8606(inputs, 1))]
                f['4b'] = (f8606[0]['15c'] + f8606[0]['18'] + f8606[0]['25c'] +
                           f8606[1]['15c'] + f8606[1]['18'] + f8606[1]['25c']) \
                           or None
            else:
                f8606 = f.addForm(F8606(inputs, None))
                f['4b'] = f8606.rowsum(['15c', '18', '25c'])

        f.comment['7a'] = 'Capital Gains'
        sd = F1040sd(inputs)
        f.addForm(sd)
        if sd.mustFile():
            f['7a'] = sd['21'] or sd['16']
        else:
            f['7a'] = inputs.get('capital_gain_dist')

        f['s1_1'] = inputs.get('state_refund_taxable')
        f.comment['s1_3'] = 'Net business income'
        f['s1_3'] = ((f.spouseSum(inputs, 'business_income') or 0) \
                        - (f.spouseSum(inputs, 'business_expenses') or 0)) or None
        f['s1_7'] = inputs.get('unemployment')

        f8889 = F8889(inputs)
        f.addForm(f8889)
        f['s1_8f'] = f8889.rowsum(['16', '20'])

        f['s1_9'] = f.rowsum(['s1_8[a-z]'])

        f['s1_10'] = f.rowsum(['s1_1', 's1_2a', 's1_[3-7]', 's1_9'])
        f.comment['8'] = 'Additional Income'
        f['8'] = f.get('s1_10')

        f.comment['s1_13'] = 'HSA deduction'
        f['s1_13'] = f8889.get('13')

        if inputs['status'] == FilingStatus.JOINT:
            if sse[0].mustFile() or sse[1].mustFile():
                f['s1_15'] = (sse[0]['13'] or 0) + (sse[1]['13'] or 0)
        else:
            if sse.mustFile():
                f['s1_15'] = sse['13']

        f['s1_25'] = f.rowsum(['s1_24[a-z]'])
        f['s1_26'] = f.rowsum(['s1_1[1-8]', 's1_19a', 's1_2[0-3]', 's1_25'])

        f.comment['6b'] = 'Taxable Social Security Benefits'
        # This line requires all of Schedule 1 and 1040 up to line 8
        f['6b'] = f.social_security_taxable(inputs)

        f.comment['9'] = 'Total Income'
        f['9'] = f.rowsum(['1z', '2b', '3b', '4b', '5b', '6b', '7a', '8'])
        f['10'] = f.get('s1_26')

        f.comment['11a'] = 'AGI'
        f['11a'] = f['9'] - f['10']
        f['11b'] = f['11a']

        # Compute the standard deduction
        std = f.STD_DED[inputs['status']]
        if inputs.get('can_be_dependent', False):
            std = min(std, max(1350, f.earned_income() + 450))
            if f.unearned_income() > 2700:
                raise RuntimeError('TODO: Kiddie Tax, form 8615')
        std += inputs.get('age_blind_boxes', 0) * f.AGE_BLIND[inputs['status']]

        sa = F1040sa(inputs, f)
        if 'itemize_deductions' in inputs:
            sa.must_file = inputs['itemize_deductions']
        else:
            sa.must_file = sa['17'] > std

        f.addForm(sa)
        f.props['itemized'] = sa.mustFile()
        if sa.mustFile():
            f.comment['12e'] = 'Itemized deductions'
            f['12e'] = sa['17']
        else:
            f.comment['12e'] = 'Standard deduction'
            f['12e'] = std

        f['s1a_1'] = f['11b']
        f['s1a_2e'] = f.rowsum(['s1a_2[abcd]'])
        f['s1a_3'] = f.rowsum(['s1a_1', 's1a_2e'])

        # TODO: no tax on tips, no tax on overtime, no tax on car loan interest

        # Enhanced Deduction for Seniors
        if inputs.get('senior', False) or inputs.get('senior_spouse', False):
            f['s1a_31'] = f['s1a_3']
            f['s1a_32'] = 150000 if inputs['status'] == FilingStatus.JOINT else 75000
            f['s1a_33'] = max(0, f['s1a_31'] - f['s1a_32'])
            f['s1a_34'] = f['s1a_33'] * .06
            f['s1a_35'] = max(0, 6000 - f['s1a_34'])
            f.props['senior phaseout'] = (f['s1a_33'] > 0 and f['s1a_35'] > 0)
            if inputs.get('senior', False):
                f['s1a_36a'] = f['s1a_35']
            if inputs.get('senior_spouse', False):
                f['s1a_36b'] = f['s1a_35']

            f.comment['s1a_37'] = 'Enhanced Deduction for Seniors'
            f['s1a_37'] = f.rowsum(['s1a_36[ab]'])

        f['s1a_38'] = f.rowsum(['s1a_13', 's1a_21', 's1a_30', 's1a_37'])

        if f['11a'] - f['s1a_13'] - f['12e'] < f.BRACKET_LIMITS[inputs['status']][3]:
            f8995 = f.addForm(F8995(inputs, f, sd))
            if f8995.mustFile():
                f['13a'] = f8995['15']
        else:
            f8995a = f.addForm(F8995A(inputs, f, sd))
            if f8995a.mustFile():
                f['13a'] = f8995a['39']

        f['13b'] = f.get('s1a_38')

        f['14'] = f['12e'] + f['13a'] + f['13b']

        f.comment['15'] = 'Taxable Income'
        f['15'] = max(0, f['11b'] - f['14'])

        # TODO: Schedule D tax worksheet
        assert(not sd['18'] and not sd['19'])
        
        f.comment['16'] = 'Regular Tax'
        f['16'] = f.div_cap_gain_tax_worksheet(inputs, sd, update_props=True)['25']

        f['s2_1z'] = f.rowsum(['s2_1[a-y]'])

        # Compute line s3_1 now because it's needed by AMT
        f.comment['s3_1'] = 'Foreign Tax Credit'
        foreign_tax = inputs.get('foreign_tax', 0)
        if foreign_tax:
            if ((foreign_tax < 300 or (foreign_tax < 600 and inputs['status'] == FilingStatus.JOINT)) \
                  and (inputs.get('foreign_tax_carryover', 0) == 0)):
                f['s3_1'] = foreign_tax
            else:
                f1116 = F1116(inputs, f, sa, sd)
                f.addForm(f1116)
                f['s3_1'] = f1116['35']

        # TODO: The second instance of sd passed to F6251 is refigured for AMT.
        # If you have a different basis in AMT for some Schedule D items, that
        # copy should be different.
        f6251 = F6251(inputs, f, sa if sa.mustFile() else None, sd, sd)
        f.comment['s2_2'] = 'AMT'
        f['s2_2'] = f6251.get('11')
        f.addForm(f6251)
        f.props['AMT'] = (f['s2_2'] > 0)

        f['s2_3'] = f.rowsum(['s2_1z', 's2_2'])

        f['17'] = f['s2_3']
        f['18'] = f['16'] + f['17']

        f8812 = F8812(inputs, f)
        f.comment['19'] = 'Child Tax Credit'
        f['19'] = f8812.get('14')
        f.addForm(f8812)

        f.comment['s3_2'] = 'Credit for child care expenses'
        f['s3_2'] = f2441.part2(f)

        f8801 = F8801(inputs, f, f6251)
        f['s3_6b'] = f8801.get('25')
        f.addForm(f8801)

        f['s3_7'] = f.rowsum(['s3_6[a-z]'])
        f['s3_8'] = f.rowsum(['s3_[1-4]', 's3_5[a-b]', 's3_7'])

        f.comment['20'] = 'Nonrefundable credits'
        f['20'] = f['s3_8']

        f.comment['21'] = 'Total Credits'
        f['21'] = f['19'] + f['20']

        f['22'] = max(0, f['18'] - f['21'])

        if inputs['status'] == FilingStatus.JOINT:
            if sse[0].mustFile() or sse[1].mustFile():
                f['s2_4'] = (sse[0]['12'] or 0) + (sse[1]['12'] or 0)
        else:
            if sse.mustFile():
                f['s2_4'] = sse['12']

        f['s2_7'] = f.rowsum(['s2_5', 's2_6'])

        f8959 = F8959(inputs, sse)
        f8960 = F8960(inputs, f, sa if sa.mustFile() else None)
        f.comment['s2_11'] = 'Additional Medicare Tax'
        f['s2_11'] = f8959['18']
        f.comment['s2_12'] = 'NIIT'
        f['s2_12'] = f8960['17'] or None
        f.addForm(f8959)
        f.addForm(f8960)
        f['s2_17c'] = f8889.get('17b')
        f['s2_17d'] = f8889.get('21')
        f['s2_18'] = f.rowsum(['s2_17[a-z]'])
        f['s2_21'] = f.rowsum(['s2_4', 's2_[7-9]', 's2_1[0-6]', 's2_1[8-9]'])

        f.comment['23'] = 'Other Taxes'
        f['23'] = f['s2_21']

        f.comment['24'] = 'Total Tax'
        f['24'] = f.rowsum(['22', '23'])

        f['25a'] = inputs.get('withholding', 0)
        f['25c'] = f8959['24']

        f.comment['25d'] = 'Withholding'
        f['25d'] = f.rowsum(['25a', '25b', '25c'])

        f.comment['26'] = 'Estimated Tax Payments'
        f['26'] = sum(inputs.get('estimated_payments', []))

        # TODO: EIC, Recovery Rebate Credit

        if inputs.get('ss_withheld'):
            if inputs['status'] == FilingStatus.JOINT:
                if inputs['ss_withheld'][0] > f.SS_MAX:
                    f['s3_11'] = inputs['ss_withheld'][0] - f.SS_MAX
                if inputs['ss_withheld'][1] > f.SS_MAX:
                    f['s3_11'] += inputs['ss_withheld'][1] - f.SS_MAX
            else:
                if inputs['ss_withheld'] > f.SS_MAX:
                    f['s3_11'] = inputs['ss_withheld'] - f.SS_MAX

        f8812.part2(inputs, f)
        f.comment['28'] = 'Additional Child Tax Credit'
        f['28'] = f8812['27']

        # Underpayment (if applicable)
        f2210 = F2210(inputs, f)
        f.addForm(f2210)

        f['s3_14'] = f.rowsum(['s3_13[a-z]'])
        f['s3_15'] = f.rowsum(['s3_9', 's3_10', 's3_11', 's3_12', 's3_14'])
        f['31'] = f['s3_15']

        f.comment['32'] = 'Refundable Credits'
        f['32'] = f.rowsum(['27a', '28', '29', '30', '31'])

        f.comment['33'] = 'Total payments'
        f['33'] = f.rowsum(['25d', '26', '32'])
        if f['33'] > f['24']:
            f.comment['34'] = 'Refund'
            f['34'] = f['33'] - f['24']
        else:
            f.comment['37'] = 'Amount you owe'
            f['37'] = f['24'] - f['33']

        #f8801_2026 = F8801_2026(inputs, f, f6251, f8801, sd)
        #f.addForm(f8801_2026)

    def tax_due(f):
        """Return the tax due on the return (negative for refund, positive for
        balance due.
        """
        return f['24'] - f['33']

    def earned_income(f):
        """Earned income for the purposes of computing the standard deduction.
        """
        return (f.rowsum(['1z', 's1_(3|6|8r|8t|8u)']) or 0) - f['s1_15']

    def unearned_income(f):
        """Unearned income for the purposes of Kiddie Tax. Note that we don't
        simply subtract earned income (above) from the AGI because certain
        income like scholarships is considered "earned" in the case of the
        standard deduction, but "unearned" in the case of Kiddie Tax
        (lines s1_8r and s1_8t).
        """
        return f['9'] + f['s1_24j'] - (f.rowsum(['1z', 's1_(3|6|8a|8d|8u|18)']) or 0)

    def div_cap_gain_tax_worksheet(f, inputs, sched_d, update_props=False):
        w = {}
        w['1'] = f['15']
        w['2'] = f['3a']
        if sched_d.mustFile():
            w['3'] = max(0, min(sched_d['15'], sched_d['16']))
        else:
            w['3'] = f['7a']
        w['4'] = w['2'] + w['3'] # dividends and cap gains
        w['5'] = max(0, w['1'] - w['4']) # ordinary income
        w['6'] = f.CAPGAIN15_LIMITS[inputs['status']]
        w['7'] = min(w['1'], w['6'])
        w['8'] = min(w['5'], w['7'])
        w['9'] = w['7'] - w['8'] # amount taxed at 0%
        w['10'] = min(w['1'], w['4'])
        w['11'] = w['9']
        w['12'] = w['10'] - w['11']
        w['13'] = f.CAPGAIN20_LIMITS[inputs['status']]
        w['14'] = min(w['1'], w['13'])
        w['15'] = w['5'] + w['9']
        w['16'] = max(0, w['14'] - w['15'])
        w['17'] = min(w['12'], w['16']) # amount taxed at 15%
        w['18'] = w['17'] * .15
        w['19'] = w['9'] + w['17']
        w['20'] = w['10'] - w['19'] # amount taxed at 20%
        w['21'] = w['20'] * .20
        w['22'], rate1 = f.tax_worksheet(inputs['status'], w['5'])
        w['23'] = w['18'] + w['21'] + w['22']
        w['24'], rate2 = f.tax_worksheet(inputs['status'], w['1'])
        w['25'] = min(w['23'], w['24'])
        if update_props:
            f.props['bracket'] = rate1 if w['23'] < w['24'] else rate2
            if w['1'] > w['13']:
                f.props['lt_gain_bracket'] = .20
                f.props['lt_gain_bump'] = (w['17'] > 0)
            elif w['1'] > w['6']:
                f.props['lt_gain_bracket'] = .15
                f.props['lt_gain_bump'] = (w['9'] > 0)
            else:
                f.props['lt_gain_bracket'] = 0
                f.props['lt_gain_bump'] = False
        return w

    def tax_worksheet(f, status, val):
        # TODO: rounding of amounts less than 100000 to match tax table
        tax = 0
        prev = 0
        i = 0
        for lim in f.BRACKET_LIMITS[status]:
            if val <= lim:
                break
            tax += f.BRACKET_RATES[i] * (lim - prev)
            prev = lim
            i += 1
        tax += f.BRACKET_RATES[i] * (val - prev)
        return tax, f.BRACKET_RATES[i]

    def social_security_taxable(f, inputs):
        w = {}
        if not f['6a']:
            return None
        w['1'] = f['6a']
        w['2'] = w['1'] * 0.5
        w['3'] = f.rowsum(['1z', '[2-5]b', '7a', '8']) or 0
        w['4'] = f['2a']
        w['5'] = w['2'] + w['3'] + w['4']
        w['6'] = f.rowsum(['s1_1[1-9]', 's1_2[035]']) or 0
        w['7'] = w['5'] - w['6']
        if w['7'] < 0:
            return 0
        w['8'] = 32000 if (inputs['status'] == FilingStatus.JOINT) else 25000
        assert(inputs['status'] != FilingStatus.SEPARATE)
        w['9'] = w['7'] - w['8']
        if w['9'] < 0:
            return 0
        w['10'] = 12000 if (inputs['status'] == FilingStatus.JOINT) else 9000
        w['11'] = max(0, w['9'] - w['10'])
        w['12'] = min(w['9'], w['10'])
        w['13'] = w['12'] / 2
        w['14'] = min(w['2'], w['13'])
        w['15'] = w['11'] * 0.85
        w['16'] = w['14'] + w['15']
        w['17'] = w['1'] * 0.85
        w['18'] = min(w['16'], w['17'])
        return w['18']

    def title(f):
        return 'Form 1040'
