from form import Form, FilingStatus
from il1040m import IL1040M
from il1040e_eitc import IL1040E_EITC
from il1040icr import IL1040ICR

class IL1040(Form):
    """
    Form IL-1040 implementation for 2024

    Developed by Stefano M. Canta (cantastefano@gmail.com).
    This software is provided without any warranty, express or implied.
    It is intended solely for the author's personal tax calculations and should not be relied upon for any other purpose.
    Use at your own risk.

    This class represents the Illinois Individual Income Tax Return (Form IL-1040) for the tax year 2024.
    It calculates Illinois state income tax based on federal AGI, Illinois-specific additions and subtractions,
    exemptions, credits, and payments.
    Required input parameters (passed via the `inputs` dictionary):
    - 'status': Filing status, must be a value from the FilingStatus enum (e.g., SINGLE, JOINT, etc.).
    - '2': Federally tax-exempt dividend and/or interest income.
    - 'C': (optional, default 0) Used for exemption calculation (see instructions for line 10a).
    - 'age_blind_boxes': (optional, default 0) Number of boxes checked for age 65 or older and/or blindness (multiplied by AGE_BLIND exemption).
    - 'dependents': (optional, default 0) Number of dependents for exemption calculation.
    - '25', '26': (optional) Payments and withholding amounts (used in lines 25 and 26).
    - Additional keys may be required by sub-forms (e.g., IL1040M, IL1040E_EITC, IL1040ICR).
    Arguments:
        inputs (dict): Dictionary of input values required for the form calculations.
        f1040 (Form): An instance of the federal Form 1040, used to obtain federal AGI and other values.
    Note:
        This implementation is intended for personal use and may not cover all edge cases or Illinois tax situations.
        It relies on several sub-forms (IL1040M, IL1040E_EITC, IL1040ICR) for specific calculations.
    """
    PERSONAL_EXEMPTION = 2775  # 2024 IL value
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

    def title(f):
        return 'Form IL-1040'