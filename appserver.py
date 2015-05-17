# coding: utf-8

"""
Application REST server for api.calendar.drevle.com

:copyright 2015 by Maxim Chernyatevich
"""

from datetime import datetime
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
from utils import CalendarDisplay


define('port', default=9001, help='run on the given port', type=int)


_calendar_fields = [
    'daily_feast', 'tone', 'saints',
    'fast', 'bows', 'julian_date',
    'gregorian_date', 'day_of_week',
    'daily_status',
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


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/(\d{4}/\d{2}/\d{2})/?', DaysHandler),
            (r'/(\d{4}/\d{2})/?', MonthHandler),
            (r'/(\d{4})/?', YearHandler),
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
            'fields', default=u",".join(i for i in _calendar_fields))
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


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()



