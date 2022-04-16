import os
import time
import socket
import json
import hashlib


print("Hello", os.environ['TYPE'], os.getpid())   # environment variable and process id


if os.environ['TYPE'] == 'master':    # create DB, if environment variable is master
    import plyvel
    db = plyvel.DB(os.environ['DB'], create_if_missing=True)


# --Master Server --
def master(env,start_response):
    key = env['REQUEST_URI'].encode('utf-8')
    metakey = db.get(key)         # ERROR HERE myb

    if metakey is None:
        if env["REQUEST_METHOD"]  == "PUT":
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
        self.basedir = os.path.realpath(basedir)
        os.makedirs(self.basedir, exist_ok=True)
        print("FileCache in %s" % basedir)


    def k2p(self, key, mkdir_ok=False):
        # must be md5 hash
        assert len(key) == 32

        path = self.basedir + "/" + key[0:2] + "/" + key[0:4]

        if not os.path.isdir(path) and mkdir_ok:
            os.makedirs(path, exist_ok=True)

        return os.path.join(path, key)


    def exists(self, key):
        return os.path.isfile(k2p(key))     # return true or false


    def delete(self, key):
        os.path.unlink(k2p(key))     # deletes the filepath


    def get(self, key):
        return open(self.k2p(key), 'rb').read()


    def put(self, key, value):
        with open(self.k2p(key, True), 'wb') as f:
            f.write(value)

if os.environ['TYPE'] == 'volume':
    host = socket.gethostname()

    # register master
    master = os.environ['MASTER']

    # create filecach
    fc = FileCache(os.environ['VOLUME'])


def volume(env,start_response):
    key = env['REQUEST_URI'].encode('utf-8')
    hkey = hashlib.md5(key).hexdigest()
    print(hkey)


    if env["REQUEST_METHOD"] == "GET":
        if not fc.exists(hkey):
            # key is not in File Cache
            start_response("404 Not Found", [('Content-type', 'text/plain')])
            return [b"Key not found"]
    return [fc.get(hkey)]


    if env["REQUEST_METHOD"] == "PUT":
        flen = int(env.get('CONTENT_LENGTH', '0'))
        fc.put(hkey, env['wsgi.input'].read(flen))


    if env["REQUEST_METHOD"] == "DELETE":
        fc.delete(hkey)



# master - server to store keys
# volume - server to store data


# db.put(b'key-%d' % time.time(), b'toms')
# for x in db.iterator():
#     print(x)

# start_response('200 OK', [('Content-Type', 'text/html')])
# return [b'Hello World']
