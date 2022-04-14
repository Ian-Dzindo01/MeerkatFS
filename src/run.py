import os
import time
import socket
import json
import hashlib


print("Hello", os.environ['TYPE'], os.getpid())   # environment variable and process id


if os.environ['TYPE'] == 'master':    # create DB
    import plyvel
    db = plyvel.DB(os.environ['DB'], create_if_missing=True)



# --Master Server --
def master(env,start_response):
    key = env['REQUEST_URI'].encode('utf-8')
    metakey = db.get(b'key')

    if metakey is None:
        if env["REQUEST_METHOD"] in ["PUT"]:
        # TODO: handle putting key
            pass

        # key doesn't exist and we arent trying to create it
        start_response("404 Not Found", [('Content-type', 'text/plain')])
        return [b"Key not found"]

    # key found
    meta = json.loads[metakey]

    # send redirect for GET or DELETE
    headers = [('location', "http://%s%s" % (meta['volume'], key)), ('expires', '0')]
    start_response("302 Found", headers)

    return [b""]




# --Volume Server --
class FileCache(object):
    def __init__(self, basedir):
        pass

    def exists(self, key):


if os.environ['TYPE'] == 'volume':
    host = socket.gethostname()

    # register master
    master = os.environ['MASTER']

    # create filecache
    fc = FileCache(os.environ['VOLUME'])


def volume(env,start_response):
    key = env['REQUEST_URI'].encode('utf-8')
    hashedkey = hashlib.md5(key).hexdigest()

    if not fc.exists(key):
        # key is not in File Cache
        start_response("404 Not Found", [('Content-type', 'text/plain')])
        return [b"Key not found"]

    return [fc.get(key)]





# master - server to store keys
# volume - server to store data


# db.put(b'key-%d' % time.time(), b'toms')
# for x in db.iterator():
#     print(x)

# start_response('200 OK', [('Content-Type', 'text/html')])
# return [b'Hello World']

