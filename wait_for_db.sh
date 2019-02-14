#!/usr/bin/env bash

if [ "${DEVELOPMENT}" == "1" ]; then
    echo "Waiting for database ..."
    while ! nc -z ${POSTGRES_HOST} ${POSTGRES_PORT}; do sleep 2; done
    echo "Connected."
fi
