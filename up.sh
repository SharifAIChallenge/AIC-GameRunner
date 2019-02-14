#!/usr/bin/env bash

if (( $# < 2 )); then
    echo "Usage: ./up.sh version port [docker-compose commands]"
fi

VERSION=$1 PORT=$2 docker-compose -f docker-compose.yml -p $1 ${@:3}
