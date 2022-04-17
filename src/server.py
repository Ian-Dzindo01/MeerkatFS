import os
import time
import json
import random
import socket
import hashlib

print("hello", os.environ['TYPE'], os.getpid())    # enivronment variable and process id

# --- Master Server ---
if os.environ['TYPE'] == "master":     # create plyvel database

  # check on volume servers
  volumes = os.environ['VOLUMES'].split(",")

  for v in volumes:
    print(v)

  import plyvel
  db = plyvel.DB(os.environ['DB'], create_if_missing=True)

def master(env, start_response):
  key = env['REQUEST_URI']        # get path component
  metakey = db.get(key.encode('utf-8')).decode('utf-8')

  if metakey is None:
    if env['REQUEST_METHOD'] == 'PUT':
      # handle put method
      # TODO: make volume selection better
      volume = random.choice(volumes)

      # save vol to database
      metakey = json.dumps({"volume": volume})   # object to json string
      db.put(key.encode('utf-8'), metakey.encode('utf-8'))

    else:
      start_response('404 Not Found', [('Content-type', 'text/plain')])
      return [b'key not found']

  else:
    # key found
    if env['REQUEST_METHOD'] == 'PUT':
      start_response('409 Conflict', [('Content-type', 'text/plain')])
      return [b'Key already exists']

    meta = json.loads(metakey.decode('utf-8'))    # json string to python dict
    volume = meta["volume"]


  # send redirect
  headers = [('location', b'http://%s%s' % (volume, key)), ('expires', '0')]
  start_response('302 Found', headers)
  return [b""]


# --- Volume Server ---
class FileCache(object):
  def __init__(self, basedir):
    self.basedir = os.path.realpath(basedir)
    os.makedirs(self.basedir, exist_ok=True)
    print("FileCache in %s" % basedir)

  def k2p(self, key, mkdir_ok=False):
    # must be MD5 hash
    assert len(key) == 32

    path = self.basedir + "/" + key[0:2] + "/" + key[0:4]

    if not os.path.isdir(path) and mkdir_ok:
      # exist ok is fine, could be a race
      os.makedirs(path, exist_ok=True)

    return os.path.join(path, key)

  def exists(self, key):
    return os.path.isfile(self.k2p(key))

  def delete(self, key):
    os.unlink(self.k2p(key))

  def get(self, key):
    return open(self.k2p(key), "rb").read()

  def put(self, key, value):
    with open(self.k2p(key, True), "wb") as f:
      f.write(value)

if os.environ['TYPE'] == "volume":
  host = socket.gethostname()

  # create the filecache
  fc = FileCache(os.environ['VOLUME'])

def volume(env, start_response):
  key = env['REQUEST_URI'].encode('utf-8')
  hkey = hashlib.md5(key).hexdigest()
  print(hkey)

  if env['REQUEST_METHOD'] == 'GET':
    if not fc.exists(hkey):
      # key not in the FileCache
      start_response('404 Not Found', [('Content-type', 'text/plain')])
      return [b'key not found']
    return [fc.get(hkey)]

  if env['REQUEST_METHOD'] == 'PUT':
    flen = int(env.get('CONTENT_LENGTH', '0'))
    fc.put(hkey, env['wsgi.input'].read(flen))

  if env['REQUEST_METHOD'] == 'DELETE':
    fc.delete(hkey)
