import coreapi
import sys

assert len(sys.argv) == 2

file = open(sys.argv[1])

credientals = {'localhost:8001': 'Token LoCaL'}
transports = [coreapi.transports.HTTPTransport(credentials=credientals)]
client = coreapi.Client(transports=transports)
schema = client.get('http://localhost:8001/api/schema/')
ans=client.action(schema,
                  ['storage','new_file','update'],
                  params={'file':coreapi.utils.File(name='file', content=file)})
print(ans['token'])
ans=client.action(schema,
                  ['run','run','create'],
                  params={'data':[{'operation':'compile','parameters':{'language':'cpp','code_zip':ans['token']}}]})
print(ans[0]['run_id'])
