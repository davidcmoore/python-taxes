from __future__ import print_function
import locale
import re

class FilingStatus:
    SINGLE=0
    JOINT=1
    SEPARATE=2
    HEAD=3
    WIDOW=4

class Form(object):
    """
    The base class for all tax forms. This acts like a dictionary but has
    some useful behaviors:
      - Values assigned in the dictionary are automatically rounded to the
        nearest integer (the "whole dollar method").
      - When missing values are retrieved with the [] operator, 0 is returned.
      - Individual lines in the form can be automatically initialized by the
        "inputs" dictionary.
    """
    def __init__(self, inputs, init_idx=None):
        self.data = {}
        self.comment = {}
        self.must_file = False
        self.forms = []
        self.disable_rounding = inputs.get('disable_rounding', False)
        name = self.__class__.__name__
        if name in inputs:
            if init_idx is not None:
                init_dict = inputs[name][init_idx]
            else:
                init_dict = inputs[name]
            for k in init_dict:
                self[k] = init_dict[k]

    def addForm(self, form):
        """
        Add another form as a child of this form. This is for later use
        by the printAllForms() method.
        """
        self.forms.append(form)
        return form

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
        elif self.disable_rounding:
            self.data[i] = float(val)
        else:
            self.data[i] = int(round(val))

    def __getitem__(self, i):
        x = self.data.get(i)
        if x is None:
            return 0
        else:
            return x

    def mustFile(self):
        """
        Returns true if this form has computed that it must be filed with
        the tax return.
        """
        return self.must_file

    def rowsum(self, rows):
        """
        Convenience function for summing a list of rows in the form by
        regex pattern. If all named rows are blank, returns None.
        """
        raw_pattern = '(' + '|'.join(rows) + ')'
        pattern = re.compile(raw_pattern)
        val = sum(v for k, v in self.data.items() if pattern.fullmatch(k))
        if any(pattern.fullmatch(k) for k, v in self.data.items()):
            return val
        return None

    def spouseSum(self, inputs, field):
        """
        Sums two spouses inputs if filing a joint return.
        """
        if field not in inputs:
            return None
        if inputs['status'] == FilingStatus.JOINT:
            return inputs[field][0] + inputs[field][1]
        else:
            return inputs[field]

    def printForm(self):
        """
        Prints all rows of a form, skipping empty rows. The rows are sorted
        sensibly.
        """
        def atoi(s):
            return int(s) if s.isdigit() else s
        def mixed_keys(s):
            return [ atoi(c) for c in re.split(r'(\d+)', s) ]

        locale.setlocale(locale.LC_ALL, '')
        print('%s:' % self.title())
        keys = list(self.data.keys())
        keys = sorted(keys, key=mixed_keys)
        for k in keys:
            print('  %6s %11s' % (k, locale.format_string('%d', self[k], grouping=True)), end='')
            if k in self.comment:
                print('  %s' % self.comment[k], end='')
            print('')

    def printAllForms(self):
        """
        Prints all child forms of this form that must be filed with the
        tax return.
        """
        for f in self.forms:
            if f.mustFile():
                f.printForm()
