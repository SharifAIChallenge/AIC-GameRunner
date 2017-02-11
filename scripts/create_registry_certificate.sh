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

exit 0

cat > ${PASSFILE} <<EOF
hello_world
hello_world
EOF




echo ">> generating a certificate authority"
  openssl genrsa -des3 \
  -passout ${PASSOPT} \
    -out ${CAKEY} 2048
  openssl req -new -x509 -days 365 \
    -batch \
    -passin ${PASSOPT} \
    -passout ${PASSOPT} \
    -key ${CAKEY} \
    -out ${CAFILE}
echo "<< certificate authority generated."

echo ".. key"
  openssl genrsa -des3 \
  -passout ${PASSOPT} \
  -out ${ROOT}/registry.key 2048

echo ".. request"
  openssl req -subj "/CN=${HOSTNAME}" -new \
    -batch \
    -key ${ROOT}/registry.key \
    -out ${ROOT}/req.csr \
    -config ${ROOT}/openssl-tmp.cnf \
    -passin ${PASSOPT} \
    -passout ${PASSOPT}

 echo ".. certificate"
  openssl x509 -req -days 365 \
    -passin ${PASSOPT} \
    -in ${ROOT}/req.csr \
    -CA ${CAFILE} \
    -CAkey ${CAKEY} \
    -CAcreateserial \
    -extensions v3_req \
    -extfile ${ROOT}/openssl-tmp.cnf \
    -out ${ROOT}/registry.crt \

  echo ".. removing key password"
  openssl rsa \
    -in ${ROOT}/registry.key \
    -out ${ROOT}/registry.key \
    -passin ${PASSOPT} \
    -passout ${PASSOPT}

echo "Cleaning up..."
rm ${ROOT}/openssl-tmp.cnf

echo "###################################################"
echo "DONE. "
echo "ca.crt must be provided to clients."
echo "registry.key and registry.crt must be used to start the registry."