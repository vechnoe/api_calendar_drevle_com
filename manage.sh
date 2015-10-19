#!/bin/sh
# Server for api.calendar.drevle.com
#
WORKDIR=.

start() {
    cd $WORKDIR
    .env/bin/python appserver.py --port=9001 --debug=false &
    echo "Server started!"
}

stop() {
    pid=`ps -ef | grep '[a]ppserver.py' | awk '{ print $2 }'`
    echo $pid
    kill $pid
    sleep 2
    echo "Server stoped!"
}

case "$1" in
  start)
    start
    ;;
  stop)
    stop
    ;;
  restart)
    stop
    start
    ;;
  *)
    echo "Usage: ./manage.sh {start|stop|restart}"
    exit 1
esac
exit 0