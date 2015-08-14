# coding: utf-8

"""
Application REST server for api.calendar.drevle.com

:copyright 2015 by Maxim Chernyatevich
"""

from datetime import datetime, date
import calendar
import dateutil.parser

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.options
from tornado.options import define, options
from tornado.web import MissingArgumentError

from tornado_cors import CorsMixin

# TODO: must be changed
from holydate import VisualPaschalion, search_feasts
from utils import CalendarDisplay, formatter


define('port', default=9001, help='run on the given port', type=int)


_fields = [
    'daily_feast', 'tone', 'saints',
    'fast', 'bows', 'julian_date',
    'gregorian_date', 'day_of_week',
    'daily_status', 'year',
    'resurrection_day', 'fast_free_weeks',
    'fasts', 'movable_feasts', 'minor_fixed_feasts',
    'major_fixed_feasts', 'soul_saturdays',
]


def _day_bundle(day, month, year, calendar, fields):
    cal = CalendarDisplay(day, month, year, calendar=calendar)
    _date = datetime(year, month, day)

    bundle = dict(
        daily_feast='get_daily_feast_as_html',
        tone='get_tone',
        saints='get_saints_as_html',
        fast='get_fast',
        bows='get_bows',
        julian_date='get_julian_date',
        gregorian_date='get_gregorian_date',
        day_of_week='get_day_of_week',
        daily_status='get_daily_status'
    )

    out = dict(date=_date.strftime("%Y-%m-%d"))
    for key, value in bundle.iteritems():
        if key in fields:
            out.update({key: getattr(cal, value).__call__()})
    return out


def _paschalion_bundle(year, calendar, fields):
    paschalion = VisualPaschalion(year, calendar=calendar)
    _date = datetime(year, 1, 1)

    bundle = dict(
        year='get_year',
        resurrection_day='get_resurrection_day',
        fast_free_weeks='get_fast_free_weeks',
        fasts='get_fasts',
        movable_feasts='get_movable_feasts',
        minor_fixed_feasts='get_minor_fixed_feasts',
        major_fixed_feasts='get_major_fixed_feasts',
        soul_saturdays='get_soul_saturdays',
    )

    out = dict(date=_date.strftime("%Y-%m-%d"))
    for key, value in bundle.iteritems():
        if key in fields:
            out.update({key: getattr(paschalion, value).__call__()})
    return out


def _search_bundle(search_string):
    result = search_feasts(search_string)

    out = dict(count=result.get('count'))

    out_list = []
    for item in result.get('result'):
        out_list.append(dict(
            gregorianDate=date(
                item[0][2], item[0][1], item[0][0]).strftime("%Y-%m-%d"),
            julianDate=date(
                item[1][2], item[1][1], item[1][0]).strftime("%Y-%m-%d"),
            searchItem=item[2].format(**formatter)
        ))

    out['result'] = out_list
    return out


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/(\d{4}/\d{2}/\d{2})/?', DaysHandler),
            (r'/(\d{4}/\d{2})/?', MonthHandler),
            (r'/(\d{4})/?', YearHandler),
            (r'/paschalion/(\d{4})/?', PaschalionHandler),
            (r'/search/?', SearchHandler),
        ]
        settings = dict(
            debug=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class CorsRequestMixin(CorsMixin):
    CORS_ORIGIN = '*'
    CORS_METHODS = 'GET'


class CalendarBaseHandler(CorsRequestMixin, tornado.web.RequestHandler):
    def get(self, slug):
        try:
            self.date = dateutil.parser.parse(slug)
        except ValueError:
            raise tornado.web.HTTPError(404, 'date invalid')

        self.calendar_system = self.get_argument(
            'calendar', default='gregorian')
        if not self.calendar_system in ['julian', 'gregorian']:
            raise tornado.web.HTTPError(404, 'calendar system not found')

        self.fields = self.get_argument(
            'fields', default=u",".join(i for i in _fields))
        self.fields = self.fields.split(',')

        self.result = dict()
        self.get_data()
        self.write(self.result)

    def get_data(self):
        return self.date, self.calendar_system, self.fields, self.result


class DaysHandler(CalendarBaseHandler):
    def get_data(self):
        self.result['day'] = []
        self.result['day'].append(
            _day_bundle(
                self.date.day, self.date.month, self.date.year,
                calendar=self.calendar_system,
                fields=self.fields
            )
        )


class MonthHandler(CalendarBaseHandler):
    def get_data(self):

        days_in_month = calendar.monthrange(
            self.date.year, self.date.month)[1] + 1

        days_list = []
        for day in range(1, days_in_month):
            days_list.append(_day_bundle(
                day, self.date.month, self.date.year,
                calendar=self.calendar_system,
                fields=self.fields
            ))

        self.result['month'] = []
        self.result['month'].append(days_list)


class YearHandler(CalendarBaseHandler):
    def get_data(self):

        months_list = []
        for month in range(1, 13):
            for day in range(1, calendar.monthrange(
                    self.date.year, month)[1] + 1):
                months_list.append(_day_bundle(
                    day, month, self.date.year,
                    calendar=self.calendar_system,
                    fields=self.fields
                ))

        self.result['year'] = []
        self.result['year'].append(months_list)


class PaschalionHandler(CalendarBaseHandler):
    def get_data(self):

        self.result['paschalion'] = []
        self.result['paschalion'].append(
            _paschalion_bundle(
                self.date.year,
                calendar=self.calendar_system,
                fields=self.fields
            )
        )


class SearchHandler(CorsRequestMixin, tornado.web.RequestHandler):
    def get(self):
        query = self.get_argument('query', '')

        result = dict(searchResult=[])
        result['searchResult'].append(
            _search_bundle(query)
        )
        self.write(result)


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()



