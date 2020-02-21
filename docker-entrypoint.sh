#!/usr/bin/env bash

if [ "${DEVELOPMENT}" == "1" ]; then
    echo "Waiting for database ..."
    while ! nc -z ${POSTGRES_HOST} ${POSTGRES_PORT}; do sleep 2; done
    echo "Connected."
fi

./manage.py migrate
if [ "${DEVELOPMENT}" == "1" ]; then
    exec ./manage.py runserver 0.0.0.0:8000
else
    ./manage.py collectstatic
    exec gunicorn -c configs/gunicorn/gunicorn.conf.py game_runner.wsgi:application
fi