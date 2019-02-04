#!/usr/bin/env bash

cat ~/Desktop/a.cpp | curl -X PUT -H "Authorization: Token salamsalam" --data-binary "@-" http://localhost:8000/api/storage/new_file/
curl -X GET -H "Authorization: Token salamsalam" http://localhost:8000/api/storage/get_file/token
curl -X POST -H "Authorization: Token test" http://$MASTER/api/game/run/