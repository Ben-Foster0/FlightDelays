class Flight:
    def __init__(self, data, airports):
        # this is gross, don't do this
        for k, v in data.items():
            setattr(self, k, v)

        self.latitude = airports[self.ORIGIN_AIRPORT]['LATITUDE']
        self.longitude = airports[self.ORIGIN_AIRPORT]['LONGITUDE']

    def get_time(self):
        return f'2015-{self.MONTH:>02}-{self.DAY:>02}T{f'{self.SCHEDULED_DEPARTURE:>04}'[0:2]}:00'
