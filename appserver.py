# coding: utf-8

"""
Application REST server for api.calendar.drevle.com
:copyright 2015 by Maxim Chernyatevich
"""
import os
import redis
from datetime import datetime
import dateutil.parser

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.options
from tornado.options import define, options

from tornado_cors import CorsMixin

from utils import day_handler, paschalion_handler, \
    search_handler, year_handler, month_handler, redis_cache


define('port', default=9001, help='run on the given port', type=int)
define('debug', default=False, help='debug mode', type=bool)

REDIS_STORAGE = redis.StrictRedis(host='localhost', port=6379, db=0)

DATE_BEGIN = datetime(1900, 1, 1)
DATE_END = datetime(2099, 12, 31)

FIELDS = [
    'dailyFeast', 'tone', 'saints',
    'fast', 'bows', 'julianDate',
    'gregorianDate', 'dayOfweek',
    'dailyStatus', 'year',
    'resurrectionDay', 'fastFreeWeeks',
    'fasts', 'movableFeasts', 'minorFixedFeasts',
    'majorFixedFeasts', 'soulSaturdays',
]


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/(\d{4}/\d{2}/\d{2})/?', DayHandler),
            (r'/(\d{4}/\d{2})/?', MonthHandler),
            (r'/(\d{4})/?', YearHandler),
            (r'/paschalion/(\d{4})/?', PaschalionHandler),
            (r'/search/?', SearchHandler),
            (r'/sm/', SimpleHandler),
        ]
        settings = dict(
            static_path=os.path.join(os.path.dirname(__file__), 'static'),
            debug=options.debug,
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

        if not DATE_END > self.date > DATE_BEGIN:
            raise tornado.web.HTTPError(404, 'date invalid')

        self.calendar_system = self.get_argument(
            'calendar', default='gregorian')
        if not self.calendar_system in ['julian', 'gregorian']:
            raise tornado.web.HTTPError(404, 'calendar system not found')

        self.fields = self.get_argument(
            'fields', default=u",".join(i for i in FIELDS))
        self.fields = self.fields.split(',')

        self.result = dict()
        self.name = None
        self.handler = None
        self.get_data()

        self.result[self.name] = redis_cache(
            REDIS_STORAGE,
            self.request.uri,
            self.handler,
            date=self.date,
            fields=self.fields,
            calendar_system=self.calendar_system
        )
        self.write(self.result)

    def get_data(self):
        pass


class DayHandler(CalendarBaseHandler):
    def get_data(self):
        self.handler = day_handler
        self.name = 'day'


class MonthHandler(CalendarBaseHandler):
    def get_data(self):
        self.handler = month_handler
        self.name = 'month'


class YearHandler(CalendarBaseHandler):
    def get_data(self):
        self.handler = year_handler
        self.name = 'year'


class PaschalionHandler(CalendarBaseHandler):
    def get_data(self):
        self.handler = paschalion_handler
        self.name = 'paschalion'


class SearchHandler(CorsRequestMixin, tornado.web.RequestHandler):
    def get(self):
        result = redis_cache(
            REDIS_STORAGE,
            self.request.uri,
            search_handler,
            query=self.get_argument('query', '')
        )
        self.write(result)


class SimpleHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('<h1>Hola!</h1>')


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()



