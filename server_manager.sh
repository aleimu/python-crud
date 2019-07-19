#!/bin/bash

config_file="uwsgi_config.ini"
log_file="./logs/python_crud_uwsgi.log"

status(){
   echo -e "\033[41;30m =========status====== \033[0m"
   ps -ef |grep $config_file|grep -v grep
   
}

start() {
    echo -e "\033[41;30m ==========start====== \033[0m"
    uwsgi --ini $config_file --daemonize $log_file
    sleep 1
    chmod 666 op_test_01.sock
}

stop() {
    echo -e "\033[41;30m ==========stop======= \033[0m"
    ps -ef |grep $config_file|grep -v grep|awk '{ if ( $3 == "1" ) print $2 }'|xargs kill -9
}

restart() {
    stop;
    sleep 1;
    start;
    status;
}

case "$1" in
    'start')
        start
        ;;
    'stop')
        stop
        ;;
    'status')
        status
        ;;
    'restart')
        restart
        ;;
    *)
    echo "usage: $0 {start|stop|restart|status}"
    exit 1
        ;;
    esac