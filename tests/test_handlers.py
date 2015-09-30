# coding: utf-8

import json
import fakeredis
from mock import patch
from datetime import date
import dateutil.parser

from tornado.testing import LogTrapTestCase, AsyncHTTPTestCase

from lib.http_test_client import HTTPClientMixin, TestClient

import appserver


def fake_handler(**kwargs):
    return dict(
        date=kwargs['date'].strftime("%Y-%m-%d"),
        calendar=kwargs['calendar_system'],
        fields=kwargs['fields']
    )


def fake_search_handler(**kwargs):
    return dict(
        count=0,
        result=[]
    )


class BaseHTTPTestCase(AsyncHTTPTestCase, HTTPClientMixin, LogTrapTestCase):
    def get_app(self):
        return appserver.Application()

    def setUp(self):
        super(BaseHTTPTestCase, self).setUp()
        self.client = TestClient(self)
        self.testdate = date(1978, 10, 5)


@patch('appserver.REDIS_STORAGE', fakeredis.FakeStrictRedis())
class HandlersTestCase(BaseHTTPTestCase):

    def setUp(self):
        super(HandlersTestCase, self).setUp()

    def test_invalid_date(self):
        """
        Check invalid date
        """
        response = self.client.get('/2110')
        self.assertEqual(response.code, 404)
        response = self.client.get('/1890')
        self.assertEqual(response.code, 404)

    @patch('appserver.day_handler', fake_handler)
    def test_DayHandler(self):
        """
        Check DayHandler calendar is gregorian
        """
        response = self.client.get(self.testdate.strftime("/%Y/%m/%d/"))
        data = json.loads(response.body)

        self.assertEqual(response.code, 200)
        self.assertEqual(data['day']['calendar'], 'gregorian')
        self.assertEqual(
            data['day']['date'], self.testdate.strftime("%Y-%m-%d"))

    @patch('appserver.day_handler', fake_handler)
    def test_DayHandler_calendar_julian(self):
        """
        Check DayHandler calendar is julian
        """
        response = self.client.get(
            self.testdate.strftime("/%Y/%m/%d/") + '?calendar=julian')
        data = json.loads(response.body)

        self.assertEqual(response.code, 200)
        self.assertEqual(data['day']['calendar'], 'julian')

    @patch('appserver.day_handler', fake_handler)
    def test_DayHandler_fields(self):
        """
        Check DayHandler fields
        """
        response = self.client.get(
            self.testdate.strftime("/%Y/%m/%d/") + '?fields=saints,tone,bows')
        data = json.loads(response.body)

        self.assertEqual(response.code, 200)
        self.assertEqual(data['day']['fields'], [u'saints', u'tone', u'bows'])

    @patch('appserver.month_handler', fake_handler)
    def test_MonthHandler(self):
        """
        Check MonthHandler
        """
        response = self.client.get(self.testdate.strftime("/%Y/%m/"))
        data = json.loads(response.body)
        _date = dateutil.parser.parse(data['month']['date'])

        self.assertEqual(response.code, 200)
        self.assertEqual(data['month']['calendar'], 'gregorian')
        self.assertListEqual(
            [_date.year, _date.month],
            [self.testdate.year, self.testdate.month]
        )

    @patch('appserver.year_handler', fake_handler)
    def test_YearHandler(self):
        """
        Check YearHandler
        """
        response = self.client.get(self.testdate.strftime("/%Y/"))
        data = json.loads(response.body)

        self.assertEqual(response.code, 200)
        self.assertEqual(
            dateutil.parser.parse(
                data['year']['date']).year, self.testdate.year)

    @patch('appserver.paschalion_handler', fake_handler)
    def test_PaschalionHandler(self):
        """
        Check PaschalionHandler
        """
        response = self.client.get(
            '/paschalion' + self.testdate.strftime("/%Y/")
        )
        data = json.loads(response.body)

        self.assertEqual(response.code, 200)
        self.assertEqual(
            dateutil.parser.parse(
                data['paschalion']['date']).year, self.testdate.year)
        self.assertEqual(data['paschalion']['calendar'], 'gregorian')

    @patch('appserver.paschalion_handler', fake_handler)
    def test_PaschalionHandler_fields(self):
        """
        Check PaschalionHandler fields
        """
        response = self.client.get(
            '/paschalion%s%s' % (
                self.testdate.strftime("/%Y/"), '?fields=soulSaturdays,fasts')
        )
        data = json.loads(response.body)
        self.assertListEqual(
            data['paschalion']['fields'], [u'soulSaturdays', u'fasts'])

    @patch('appserver.search_handler', fake_search_handler)
    def test_SearchHandler(self):
        """
        Check SearchHandler
        """
        response = self.client.get(u'/search?query=Нил')
        self.assertEqual(response.code, 200)
        data = json.loads(response.body)
        self.assertDictEqual(data, {u'count': 0, u'result': []})








