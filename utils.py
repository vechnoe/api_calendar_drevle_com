# coding: utf-8

import hashlib
import calendar
from datetime import datetime, date
import cPickle as pickle

from holydate import AncientCalendar, VisualPaschalion, search_feasts


FORMATTER = dict(
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


def hashkey(string):
    hasher = hashlib.sha1()
    hasher.update(string)
    return hasher.hexdigest()


def redis_cache(redis_storage, key, handler, **kwargs):
    key = hashkey(key)

    if redis_storage.exists(key):
        return pickle.loads(redis_storage.get(key))

    result = handler(**kwargs)
    pickled_object = pickle.dumps(result)
    redis_storage.set(key, pickled_object)
    return result


def day_handler(**kwargs):
    date = kwargs['date']

    cal = AncientCalendar(
        date.day, date.month, date.year, calendar=kwargs['calendar_system'])
    _date = datetime(date.year, date.month, date.day)

    bundle = dict(
        dailyFeast='get_daily_feast',
        tone='get_tone',
        saints='get_saints',
        fast='get_fast',
        bows='get_bows',
        julianDate='get_julian_date',
        gregorianDate='get_gregorian_date',
        dayOfWeek='get_day_of_week'
    )

    out = dict(date=_date.strftime("%Y-%m-%d"))
    for key, value in bundle.iteritems():
        if key in kwargs['fields']:
            out.update({key: getattr(
                cal, value).__call__().format(**FORMATTER)})
    return out


def paschalion_handler(**kwargs):
    year = kwargs['date'].year
    paschalion = VisualPaschalion(year, calendar=kwargs['calendar_system'])
    _date = datetime(year, 1, 1)

    bundle = dict(
        year='get_year',
        resurrectionDay='get_resurrection_day',
        fastFreeWeeks='get_fast_free_weeks',
        fasts='get_fasts',
        movableFeasts='get_movable_feasts',
        minorFixedFeasts='get_minor_fixed_feasts',
        majorFixedFeasts='get_major_fixed_feasts',
        soulSaturdays='get_soul_saturdays',
    )

    out = dict(date=_date.strftime("%Y-%m-%d"))
    for key, value in bundle.iteritems():
        if key in kwargs['fields']:
            out.update({key: getattr(paschalion, value).__call__()})
    return out


def month_handler(**kwargs):
    _date = kwargs['date']
    out = []

    for day in range(1, calendar.monthrange(_date.year, _date.month)[1] + 1):
        out.append(
            day_handler(
                date=date(_date.year, _date.month, day),
                calendar_system=kwargs['calendar_system'],
                fields=kwargs['fields']
            ))
    return out


def year_handler(**kwargs):
    _date = kwargs['date']
    out = []

    for month in range(1, 13):
        for day in range(1, calendar.monthrange(_date.year, month)[1] + 1):
            out.append(
                day_handler(
                    date=date(_date.year, month, day),
                    calendar_system=kwargs['calendar_system'],
                    fields=kwargs['fields']
                ))
    return out


def search_handler(**kwargs):
    result = search_feasts(kwargs['query'])
    out = dict(count=result.get('count'))

    out_list = []
    for item in result.get('result'):
        # FIXME:
        try:
            out_list.append(dict(
                gregorianDate=date(
                    item[1][2], item[1][1], item[1][0]).strftime("%Y-%m-%d"),
                julianDate=date(
                    item[0][2], item[0][1], item[0][0]).strftime("%Y-%m-%d"),
                searchItem=item[2].format(**FORMATTER)
            ))
        except ValueError:
            pass

    out['result'] = out_list
    return out
