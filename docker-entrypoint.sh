#!/usr/bin/env bash

if [ "${DEVELOPMENT}" == "1" ]; then
    echo "Waiting for database ..."
    while ! nc -z ${POSTGRES_HOST} ${POSTGRES_PORT}; do sleep 2; done
    echo "Connected."
fi

if [ "${DEVELOPMENT}" == "1" ]; then
    exec ./manage.py runserver 0.0.0.0:8000
else
    exec gunicorn -c configs/gunicorn/gunicorn.conf.py game_runner.wsgi:application
fi