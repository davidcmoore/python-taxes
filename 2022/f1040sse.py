from form import Form

SS_WAGE_LIMIT = 147000

# Not implemented: optional methods
class F1040sse(Form):
    def __init__(self, inputs):
        super(F1040sse, self).__init__(inputs)
        self['2'] = inputs.get('business_income')
        self['3'] = self.rowsum(['1a', '1b', '2'])
        if self['3'] > 0:
            self['4a'] = self['3'] * 0.9235
        else:
            self['4a'] = self['3']
        self['4c'] = self.rowsum(['4a', '4b'])
        if self['4c'] < 400:
            return
        self.must_file = True
        self['6'] = self.rowsum(['4c', '5b'])
        self['7'] = SS_WAGE_LIMIT
        self['8a'] = inputs['wages_ss']
        if self['8a'] < SS_WAGE_LIMIT:
            self['8d'] = self.rowsum(['8a', '8b', '8c'])
            self['9'] = self['7'] - self['8d']
            if self['9'] <= 0:
                self['9'] = 0
                self['10'] = 0
            else:
                self['10'] = min(self['6'], self['9']) * .124
        self['11'] = self['6'] * .029
        self['12'] = self.rowsum(['10', '11'])
        self['13'] = self['12'] * .5

    def title(self):
        return 'Schedule SE'
