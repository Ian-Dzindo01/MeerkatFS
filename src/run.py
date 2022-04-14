import os
import time
import socket
import json


print("Hello", os.environ['TYPE'], os.getpid())


if os.environ['TYPE'] == 'master':
    import plyvel
    db = plyvel.DB(os.environ['DB'], create_if_missing=True)

# --Master Server --

def master(env,start_response):
    key = env['REQUEST_URI'].encode('utf-8')
    metakey = db.get(b'key')


    if metakey is None:
        # key doesn't exist
        start_response("404 Not Found", [('Content-type', 'text/plain')])
        return [b"Key not found"]


    # key found: volume
    meta = json.loads[metakey]

    # send redirect
    headers = [('location', "http://%s%s" % (meta['volume'], key)), ('expires', '0')]
    start_response("302 Found", headers)
        return [b""]

# --Volume Server --

if os.environ['TYPE'] == 'volume':
    host = socket.gethostname()


def volume(env,start_response):
    print(os.getpid())
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [b'Nope world']


# master - server to store keys
# volume - server to store data


# db.put(b'key-%d' % time.time(), b'toms')
# for x in db.iterator():
#     print(x)

# start_response('200 OK', [('Content-Type', 'text/html')])
# return [b'Hello World']

