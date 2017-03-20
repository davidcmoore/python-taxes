from form import Form

SS_WAGE_LIMIT = 118500

# Not implemented: optional methods
class F1040sse(Form):
    def __init__(self, inputs):
        def useLong(inputs):
            wages = inputs.get('wages', 0)
            if wages > 0:
                if inputs['wages_ss'] + inputs.get('business_income', 0) > SS_WAGE_LIMIT:
                    return True
            return False

        super(F1040sse, self).__init__(inputs)
        if not useLong(inputs):
            self['A2'] = inputs.get('business_income')
            self['A3'] = self.rowsum(['A1a', 'A1b', 'A2'])
            self['A4'] = self['A3'] * 0.9235
            if self['A4'] < 400:
                return
            self.must_file = True
            if self['A4'] <= SS_WAGE_LIMIT:
                self['A5'] = self['A4'] * .153
            else:
                self['A5'] = self['A4'] * .029 + SS_WAGE_LIMIT * .124
            self['A6'] = self['A5'] * .50
        else:
            self['B2'] = inputs.get('business_income')
            self['B3'] = self.rowsum(['B1a', 'B1b', 'B2'])
            if self['B3'] > 0:
                self['B4a'] = self['B3'] * 0.9235
            else:
                self['B4a'] = self['B3']
            self['B4c'] = self.rowsum(['B4a', 'B4b'])
            if self['B4c'] < 400:
                return
            self.must_file = True
            self['B6'] = self.rowsum(['B4c', 'B5b'])
            self['B7'] = SS_WAGE_LIMIT
            self['B8a'] = inputs['wages_ss']
            if self['B8a'] < SS_WAGE_LIMIT:
                self['B8d'] = self.rowsum(['B8a', 'B8b', 'B8c'])
                self['B9'] = self['B7'] - self['B8d']
                if self['B9'] <= 0:
                    self['B9'] = 0
                    self['B10'] = 0
                else:
                    self['B10'] = min(self['B6'], self['B9']) * .124
            self['B11'] = self['B6'] * .029
            self['B12'] = self.rowsum(['B10', 'B11'])
            self['B13'] = self['B12'] * .5

    def title(self):
        return 'Schedule SE'
