from form import Form, FilingStatus
from f1040 import F1040
from ca540sca import CA540sca
from ca540sp import CA540sp
import math

class CA540(Form):
    EXEMPTION = 118
    DEPENDENT_EXEMPTION = 367
    BRACKET_RATES = [.01, .02, .04, .06, .08, .093, .103, .113, .123]
    BRACKET_LIMITS = [
        [8544, 20255, 31969, 44377, 56085, 286492, 343788, 572980],   # SINGLE
        [17088, 40510, 63938, 88754, 112170, 572984, 687576, 1145960],# JOINT
        [8544, 20255, 31969, 44377, 56085, 286492, 343788, 572980],   # SEPARATE
        [17099, 40512, 52224, 64632, 76343, 389627, 467553, 779253],  # HEAD
        [17088, 40510, 63938, 88754, 112170, 572984, 687576, 1145960],# WIDOW
    ]
    SDI_MAX = 1149.67
    MENTAL_HEALTH_LIMIT = 1000000
    MENTAL_HEALTH_RATE = .01

    def __init__(f, inputs, f1040):
        super(CA540, f).__init__(inputs)
        f.must_file = True
        f.addForm(f)

        for i in f1040.forms:
            if i.__class__.__name__ == 'F1040sa':
                f1040sa = i

        if inputs['status'] in [FilingStatus.JOINT, FilingStatus.WIDOW]:
            personal = 2
        else:
            personal = 1

        f['7'] = personal * f.EXEMPTION
        # TODO: blind or senior
        f['10'] = (inputs['exemptions'] - personal) * f.DEPENDENT_EXEMPTION
        f['11'] = f.rowsum(['7', '8', '9', '10'])

        f['12'] = f.spouseSum(inputs, 'wages')
        f.comment['13'] = 'Federal AGI'
        f['13'] = f1040['8b']
        sca = f.addForm(CA540sca(inputs, f1040, f1040sa))
        f['14'] = sca['B37']
        f['15'] = f['13'] - f['14']
        f['16'] = sca['C37']
        f.comment['17'] = 'CA AGI'
        f['17'] = f['15'] + f['16']
        f['18'] = sca['II30']
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
        f['72'] = inputs.get('state_estimated_payments')
        # TODO: real estate withholding
        if inputs.get('ca_sdi_withheld'):
            if inputs['status'] == FilingStatus.JOINT:
                if inputs['ca_sdi_withheld'][0] > f.SDI_MAX:
                    f['74'] = inputs['ca_sdi_withheld'][0] - f.SDI_MAX
                if inputs['ca_sdi_withheld'][1] > f.SDI_MAX:
                    f['74'] += inputs['ca_sdi_withheld'][1] - f.SDI_MAX
            else:
                if inputs['ca_sdi_withheld'] > f.SDI_MAX:
                    f['74'] = inputs['ca_sdi_withheld'] - f.SDI_MAX
        f.comment['76'] = 'Total payments'
        f['76'] = f.rowsum(['71', '72', '73', '74', '75'])

        if f['76'] > f['91']:
            f['92'] = f['76'] - f['91']
        else:
            f['93'] = f['91'] - f['76']

        if f['92'] > f['64']:
            f.comment['94'] = 'Refund'
            f['94'] = f['92'] - f['64']
        else:
            f.comment['97'] = 'Tax due'
            f['97'] = f['64'] - f['92']
        f.comment['111'] = 'Amount you owe'
        f['111'] = f.rowsum(['93', '97', '110'])

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
        LIMITS = [194504, 389013, 194504, 291760, 389013]
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
