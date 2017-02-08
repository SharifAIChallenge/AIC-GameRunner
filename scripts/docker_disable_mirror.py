import os
import sys
import re

import subprocess

has_opt = False

try:
    with open('/etc/default/docker.tmp', 'w') as fout:
        with open('/etc/default/docker') as fin:
            for line in fin:
                if line.startswith("DOCKER_OPTS="):
                    has_opt = True
                    if '--registry-mirror=' in line:
                        line = re.sub(pattern=r'--registry-mirror=.*? ',
                                      repl='', string=line)
                        line = re.sub(pattern=r'--registry-mirror=.*?"',
                                      repl='"', string=line)
                    if '--insecure-registry=' in line:
                        line = re.sub(pattern=r'--insecure-registry=.*? ', #84 200 16 245
                                      repl='', string=line)
                        line = re.sub(pattern=r'--insecure-registry=.*?"', #84 200 16 245
                                      repl='"', string=line)
                fout.write(line)
    os.rename('/etc/default/docker.tmp', '/etc/default/docker')
    process = subprocess.call(['sudo', 'service', 'docker', 'restart'])
except IOError as e:
    print e.strerror
