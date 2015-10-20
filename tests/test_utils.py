# coding: utf-8

"""
Unittests for utils
"""

import datetime
import unittest

import fakeredis
from mock import patch, call

from utils import hashkey, redis_cache, day_handler, month_handler, \
    year_handler, paschalion_handler, search_handler


def fake_handler(**kwargs):
    return kwargs


def fake_search_feasts(string):
    return dict(
        count=1,
        result=[[
            [1, 9, 2015],
            [14, 9, 2015],
            u'Lorem {highlight_start}ipsum{highlight_end} dolor sit amet']]
    )


class UtilsTestCase(unittest.TestCase):

    def setUp(self):
        self.redis_storage = fakeredis.FakeStrictRedis()
        self.handler = fake_handler
        self.date = datetime.date(2015, 1, 1)
        self.fields = [
            'date', 'tone', 'bows', 'fast', 'dayOfWeek', 'dailyFeast']
        self.paschalion_fields = [
            'date', 'resurrectionDay', 'fastFreeWeeks', 'fasts'
        ]

    def test_hashkey(self):
        """
        Check hashkeys equality
        """
        hash1 = hashkey('lorem ipsum dolor sit')
        hash2 = hashkey('lorem ipsum dolor sit')
        self.assertEqual(hash1, hash2)

    def test_redis_cache(self):
        """
        Check redis fetching and storing
        """
        key = 'baz'
        cache = redis_cache(
            self.redis_storage, key, self.handler, foo='foo', bar='bar'
        )
        # When key not exist in storage
        self.assertDictEqual({'foo': 'foo', 'bar': 'bar'}, cache)
        # The key exist
        self.assertTrue(self.redis_storage.exists(hashkey(key)))

    @patch('utils.AncientCalendar')
    def test_day_handler(self, mock_calendar):
        """
        Check fields in day_handler returns
        """
        out = day_handler(
            calendar_system='gregorian', date=self.date, fields=self.fields)
        calls = [
            call().get_tone(), call().get_bows(),
            call().get_fast(), call().get_daily_feast()
        ]
        mock_calendar.assert_has_calls(calls, any_order=True)
        self.assertEqual(out['date'], '2015-01-01')
        for k in out.iterkeys():
            self.assertIn(k, self.fields)

    def test_month_handler(self):
        """
        Check count key:value pairs in month_handler dict returns
        """
        out = month_handler(
            calendar_system='gregorian', date=self.date, fields=self.fields)
        self.assertEqual(31, len(out))

    def test_year_handler(self):
        """
        Check count key:value pairs in year_handler dict returns
        """
        out = year_handler(
            calendar_system='gregorian', date=self.date, fields=self.fields)
        self.assertEqual(365, len(out))

    @patch('utils.VisualPaschalion')
    def test_paschalion_handler(self, mock_paschalion):
        """
        Check fields & method calls in paschalion_handler returns
        """
        out = paschalion_handler(
            calendar_system='gregorian',
            date=self.date,
            fields=self.paschalion_fields
        )
        calls = [
            call().get_resurrection_day(),
            call().get_fast_free_weeks(),
            call().get_fasts()
        ]

        mock_paschalion.assert_has_calls(calls, any_order=True)
        self.assertEqual(out['date'], '2015-01-01')
        for k in out.iterkeys():
            self.assertIn(k, self.paschalion_fields)

    @patch('utils.search_feasts', fake_search_feasts)
    def test_search_handler(self):
        """
        Check search_handler output dates & result highlighting
        """
        out = search_handler(query=u'Lorem')
        self.assertEqual(
            out['result'][0]['searchItem'],
            u'Lorem <span class="highlight">ipsum</span> dolor sit amet'
        )
        self.assertEqual(out['result'][0]['julianDate'], '2015-09-01')
        self.assertEqual(out['result'][0]['gregorianDate'], '2015-09-14')

if __name__ == '__main__':
    unittest.main()


