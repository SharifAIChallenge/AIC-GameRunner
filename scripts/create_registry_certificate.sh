#!/usr/bin/env bash
# Based on
# https://gist.github.com/jhamrick/ac0404839b5c7dab24b5


if [[ $# -ne 1 ]];
then
    echo "Usage: create_registry_certificate.sh <ip>"
    exit 1
fi

ROOT="$(pwd)/certs"
CAFILE="${ROOT}/ca.crt"
CAKEY="${ROOT}/ca.key"
PASSFILE="${ROOT}/pass"
PASSOPT="file:$PASSFILE"

echo "Cleaning previous certificates"
rm -rf $ROOT
mkdir -p $ROOT

cp openssl.cnf ${ROOT}/openssl-tmp.cnf
echo "IP.1 = $1" >> ${ROOT}/openssl-tmp.cnf

openssl req \
 -newkey rsa:4096 -nodes -sha256 -keyout ${ROOT}/registry.key \
 -x509 -days 365 -out ${ROOT}/registry.crt -extensions v3_req -config  ${ROOT}/openssl-tmp.cnf
