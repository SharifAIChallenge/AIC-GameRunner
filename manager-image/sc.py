import yaml
import sys
a = yaml.load(open('docker-compose.yml'))
for name in a['services']: 
    if not 'deplpy' in a['services'][name] :
        a['services'][name]['deploy'] = {}
    a['services'][name]['deploy']['placement'] = {}
    a['services'][name]['deploy']['placement']['constraints'] = [ 'node.id == ' + sys.argv[1] ] 
    a['services'][name]['deploy']['restart_policy'] = {}
    a['services'][name]['deploy']['restart_policy']['condition'] = 'none'

print( yaml.dump(a) )
