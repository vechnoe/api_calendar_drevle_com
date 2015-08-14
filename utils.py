# coding: utf-8

from holydate import AncientCalendar, menology

formatter = dict(
    red=u'<span class="red">',
    bold=u'<span class="bold">',
    end=u'</span>',
    tw=u'<span class="twelve">ӱ</span>',
    pl=u'<span class="polyeleos">Ӱ</span>',
    gl=u'<span class="glorium">Ӵ</span>',
    sx=u'<span class="six">Ӵ</span>',
    redgui=u'',
    highlight_start=u'<span class="highlight">',
    highlight_end=u'</span>'
)


class CalendarDisplay(AncientCalendar):
    """
    Оverride some methods with reformat.
    """

    def get_daily_feast_as_html(self):
        return self.get_daily_feast().format(**formatter)

    def get_saints_as_html(self):
        return self.get_saints().format(**formatter)

    def get_daily_status(self):
        """
        Get daily feast and fest status for gui-calendar.
        """

        #_day = menology.menology[self.__month][self.__day]
        #_saint = _day.get('saint')
        #_daily_feast = self.get_daily_feast()
        #self.get_fast()
        #weekday = self.get_day_of_week(verbose=False)
#
        #gl = u'{gl}'
        #pl = u'{pl}'
        #tw = u'{tw}'
        #redgui = u'{redgui}'
#
        ##Sunday.
        #if weekday in [0] and self.fast in [6, 7, 8, 9, 10, 11, 12, 13]:
        #    index = 'feast'  # Feast.
        #elif weekday in [0] and self.fast in [0, 1, 2, 3, 4, 5, 14]:
        #    index = 'fast_and_feast'  # Feast and fast.
        ##Feast.
        #elif gl in _daily_feast and self.fast in [6, 7, 8, 9, 10, 11, 12, 13]:
        #    index = 'feast'
        #elif pl in _daily_feast and self.fast in [6, 7, 8, 9, 10, 11, 12, 13]:
        #    index = 'feast'
        #elif tw in _daily_feast and self.fast in [6, 7, 8, 9, 10, 11, 12, 13]:
        #    index = 'feast'
        #elif _saint in [2, 3, 4, 5, 6, 7] \
        #        and self.fast in [6, 7, 8, 9, 10, 11, 12, 13]:
        #    index = 'feast'
        ##Feast and fast.
        #elif gl in _daily_feast and self.fast in [0, 1, 2, 3, 4, 5, 14]:
        #    index = 'fast_and_feast'
        #elif pl in _daily_feast and self.fast in [0, 1, 2, 3, 4, 5, 14]:
        #    index = 'fast_and_feast'
        #elif tw in _daily_feast and self.fast in [0, 1, 2, 3, 4, 5, 14]:
        #    index = 'fast_and_feast'
        #elif _saint in [2, 3, 4, 5, 6, 7] \
        #        and self.fast in [0, 1, 2, 3, 4, 5, 14]:
        #    index = 'fast_and_feast'
        ##Fast.
        #elif _saint in [0, 1] and self.fast in [0, 1, 2, 3, 4, 5, 14]:
        #    index = 'fast'
        ##Easter.
        #elif redgui in _daily_feast:
        #    index = 'feast'  # Feast.
        #else:
        #    index = 'ordinary'  # Ordinary day.
        #return index
        import random
        return random.choice(['fast', 'feast', 'ordinary', 'fast_and_feast'])