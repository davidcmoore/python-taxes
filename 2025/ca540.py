from form import Form, FilingStatus
from f1040 import F1040
from ca5805 import CA5805
from ca540sca import CA540sca
from ca540sp import CA540sp
import math

class CA540(Form):
    EXEMPTION = 153
    DEPENDENT_EXEMPTION = 475
    BRACKET_RATES = [.01, .02, .04, .06, .08, .093, .103, .113, .123]
    BRACKET_LIMITS = [
        [11079, 26264, 41452, 57542, 72724, 371479, 445771, 742953],  # SINGLE
        [22158, 52528, 82904, 115084, 145448, 742958, 891542, 1485906],# JOINT
        [11079, 26264, 41452, 57542, 72724, 371479, 445771, 742953],  # SEPARATE
        [22173, 52530, 67716, 83805, 98990, 505208, 606251, 1010417], # HEAD
        [22158, 52528, 82904, 115084, 145448, 742958, 891542, 1485906],# WIDOW
    ]
    MENTAL_HEALTH_LIMIT = 1000000
    MENTAL_HEALTH_RATE = .01

    def __init__(f, inputs, f1040=None):
        super(CA540, f).__init__(inputs)
        f.must_file = True
        f.addForm(f)

        if f1040 is None:
            f1040 = F1040(inputs)

        for i in f1040.forms:
            if i.__class__.__name__ == 'F1040sa':
                f1040sa = i

        if inputs.get('can_be_dependent', False):
            personal = 0
        elif inputs['status'] in [FilingStatus.JOINT, FilingStatus.WIDOW]:
            personal = 2
        else:
            personal = 1

        f['7'] = personal * f.EXEMPTION
        f['8'] = inputs.get('age_blind_boxes', 0) * f.EXEMPTION or None
        f['10'] = (inputs['exemptions'] - personal) * f.DEPENDENT_EXEMPTION
        f['11'] = f.rowsum(['7', '8', '9', '10'])

        # Line 12 is just informational. Leave it out of our computations.
        f.comment['13'] = 'Federal AGI'
        f['13'] = f1040['11b']
        sca = f.addForm(CA540sca(inputs, f1040, f1040sa))
        f.comment['14'] = 'CA Subtractions'
        f['14'] = sca['1C_B27']
        f['15'] = f['13'] - f['14']
        f.comment['16'] = 'CA Additions'
        f['16'] = sca['1C_C27']
        f.comment['17'] = 'CA AGI'
        f['17'] = f['15'] + f['16']
        f.comment['18'] = 'Standard or Itemized Deduction'
        f['18'] = sca['2_30']
        f.comment['19'] = 'Taxable income'
        f['19'] = max(0, f['17'] - f['18'])

        f.comment['31'] = 'Tax'
        f['31'] = f.tax_rate_schedule(inputs['status'], f['19'])
        f['32'] = f.agi_limitation_worksheet(inputs['status'])
        f['33'] = max(0, f['31'] - f['32'])
        f['35'] = f['33'] + f['34']

        f['47'] = f.rowsum(['40', '43', '44', '45', '46'])
        f['48'] = max(0, f['35'] - f['47'])

        sp = f.addForm(CA540sp(inputs, f, sca, f1040, f1040sa))
        f['61'] = sp.get('26')
        f.comment['61'] = 'AMT'

        if f['19'] > f.MENTAL_HEALTH_LIMIT:
            f['62'] = (f['19'] - f.MENTAL_HEALTH_LIMIT) * f.MENTAL_HEALTH_RATE
        f.comment['64'] = 'Total tax'
        f['64'] = f.rowsum(['48', '61', '62', '63'])

        f['71'] = inputs.get('state_withholding')
        f['72'] = sum(inputs.get('state_estimated_payments', []))
        # TODO: real estate withholding

        f.comment['78'] = 'Total payments'
        f['78'] = f.rowsum(['71', '72', '73', '74', '75', '76', '77'])

        if f['78'] > f['91']:
            f['93'] = f['78'] - f['91']
        else:
            f['94'] = f['91'] - f['78']

        if f['93'] > f['92']:
            f['95'] = f['93'] - f['92']
        else:
            f['96'] = f['92'] - f['93']

        if f['95'] > f['64']:
            f.comment['97'] = 'Refund'
            f['97'] = f['95'] - f['64']
        else:
            f.comment['100'] = 'Tax due'
            f['100'] = f['64'] - f['95']
        f.comment['111'] = 'Amount you owe'
        f['111'] = f.rowsum(['94', '96', '100', '110'])

        ca5805 = CA5805(inputs, f)
        f.addForm(ca5805)

    def tax_due(f):
        """Return the tax due on the return (negative for refund, positive for
        balance due.
        """
        return f['64'] - f['95']

    @classmethod
    def tax_rate_schedule(f, status, val):
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
        return tax

    def agi_limitation_worksheet(f, status):
        LIMITS = [252203, 504411, 252203, 378310, 504411]
        w = {}
        w['a'] = f['13']
        w['b'] = LIMITS[status]
        if w['a'] <= w['b']:
            return f['11']
        w['c'] = w['a'] - w['b']
        divisor = 1250.00 if status == FilingStatus.SEPARATE else 2500.00
        w['d'] = math.ceil(w['c'] / divisor)
        w['e'] = w['d'] * 6
        w['f'] = (f['7'] + f['8'] + f['9']) / f.EXEMPTION
        w['g'] = w['e'] * w['f']
        w['h'] = f['7'] + f['8'] + f['9']
        w['i'] = max(0, w['h'] - w['g'])
        w['j'] = f['10'] / f.DEPENDENT_EXEMPTION
        w['k'] = w['e'] * w['j']
        w['l'] = f['10']
        w['m'] = max(0, w['l'] - w['k'])
        w['n'] = w['i'] + w['m']
        return w['n']

    def title(f):
        return 'CA Form 540'
