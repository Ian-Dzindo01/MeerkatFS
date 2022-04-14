import os
import time

print("Hello", os.environ['TYPE'], os.getpid())

if os.environ['TYPE'] == 'master':
    import plyvel
    db = plyvel.DB(os.environ['DB'], create_if_missing=True)

def master(env,start_response):
    print(os.getpid())
    print(db)
    db.put(b'key-%d' % time.time(), b'tom')
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [b'Hello World']

def volume(env,start_response):
    print(os.getpid())
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [b'Nope world']


# master - server to store keys
# volume - server to store data
# minute 35
