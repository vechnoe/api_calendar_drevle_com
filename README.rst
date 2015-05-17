api.calendar.drevle.com
=======================

Description
-----------
Application REST server for api.calendar.drevle.com
Supports only GET requests. 

Usage
-----
Server runs on 9001 port:

    make run
     
Get all days and all fields in whole year:
    
    curl http://localhost:9001/2015/
    
Just a month:
    
    curl http://localhost:9001/2015/05
    
And day:
    
    curl http://localhost:9001/2015/05/17

Only separate fields:
    
    curl http://localhost:9001/2015/05/17?fields="bows,tone"
    
Authors
-------

* Author: `Maxim Chernyatevich`_

.. _`Maxim Chernyatevich`: https://github.com/vechnoe


Dependencies
------------

*Required*

* `Python 2.7.x. <http://python.org/download/>`_

* `Tornado 4.x.x. <https://pypi.python.org/pypi/tornado/>`_

* `Tornado-cors <https://pypi.python.org/pypi/tornado-cors/>`_

* `Holydate  <https://pypi.python.org/pypi/holydate/>`_

* `Python-dateutil <https://pypi.python.org/pypi/python-dateutil/>`_


    
