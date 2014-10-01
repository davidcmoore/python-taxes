import locale

class FilingStatus:
    SINGLE=0
    JOINT=1
    SEPARATE=2
    HEAD=3
    WIDOW=4

class Form(object):
    def __init__(self, inputs):
        self.data = {}
        self.must_file = False
        self.forms = []
        name = self.__class__.__name__
        if name in inputs:
            for k in inputs[name]:
                self[k] = inputs[name][k]

    def addForm(self, form):
        if form.mustFile():
            self.forms.append(form)

    def get(self, i):
        if i in self.data:
            return self.data[i]
        else:
            return None

    def __contains__(self, i):
        return i in self.data

    def __setitem__(self, i, val):
        if val is None:
            if i in self.data:
                del self.data[i]
        else:
            self.data[i] = int(round(val))

    def __getitem__(self, i):
        x = self.data.get(i)
        if x is None:
            return 0
        else:
            return x

    def mustFile(self):
        return self.must_file

    def rowsum(self, rows):
        val = 0
        isNone = True
        for r in rows:
            if r in self:
                isNone = False
                val += self[r]
        return None if isNone else val

    def spouseSum(self, inputs, field):
        if field not in inputs:
            return None
        if inputs['status'] == FilingStatus.JOINT:
            return inputs[field][0] + inputs[field][1]
        else:
            return inputs[field]

    def printForm(self):
        def keynormalize(a):
            s = ''
            numstr = ''
            out = []
            for c in a:
                if c.isdigit():
                    if s:
                        out.append(s)
                        s = ''
                    numstr += c
                else:
                    if numstr:
                        out.append(int(numstr))
                        numstr = ''
                    s += c
            if s:
                out.append(s)
            if numstr:
                out.append(int(numstr))
            return out

        locale.setlocale(locale.LC_ALL, '')
        print('%s:' % self.title())
        keys = self.data.keys()
        keys.sort(key=keynormalize)
        for k in keys:
            print('  %4s %11s' % (k, locale.format('%d', self[k], 1)))

    def printAllForms(self):
        for f in self.forms:
            f.printForm()
