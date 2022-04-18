import os
import time
import json
import random
import socket
import hashlib

print("hello", os.environ['TYPE'], os.getpid())    # hello environment variable and process id


def resp(sr, code, resp, headers=[('Content-type', 'text/plain')], body=b''):
  sr(code, headers)
  return [b'']

# --- Master Server ---
if os.environ['TYPE'] == "master":
  volumes = os.environ['VOLUMES'].split(",")    # volume servers

  for v in volumes:
    print(v)

  import plyvel
  db = plyvel.DB(os.environ['DB'], create_if_missing=True)    # create database


def master(env, sr):
  key = env['REQUEST_URI']       # URI env var
  metakey = db.get(key.encode('utf-8'))

  if metakey is None:
    if env['REQUEST_METHOD'] == 'PUT':
      # TODO: make volume selection intelligent
      volume = random.choice(volumes)

      meta = {"volume": volume}    # save vol to db

      db.put(key.encode('utf-8'), json.dumps(meta).encode('utf-8'))
    else:
      # this key doesn't exist and we aren't trying to create it
      return resp(sr, '404 Not Found')

  else:
    # key found and we are trying to put it
    """
    if env['REQUEST_METHOD'] == 'PUT':
      return resp(sr, '409 Conflict')
    """

    meta = json.loads(metakey.decode('utf-8'))

  # send redirect
  print(meta)
  volume = meta['volume']
  headers = [('Location', 'http://%s%s' % (volume, key))]
  return resp(sr, '307 Temporary Redirect', headers)
  return [b""]


# --- Volume Server ---
class FileCache(object):
  def __init__(self, basedir):
    self.basedir = os.path.realpath(basedir)
    os.makedirs(self.basedir, exist_ok=True)
    print("FileCache in %s" % basedir)


  def k2p(self, key, mkdir_ok=False):
    # MD5 hash
    assert len(key) == 32

    path = self.basedir + "/" +key[0:2] + "/" + key[0:4]   # how do you get this combo?
    if not os.path.isdir(path) and mkdir_ok:
      os.makedirs(path, exist_ok=True)

    return os.path.join(path, key)


  def exists(self, key):
    return os.path.isfile(self.k2p(key))


  def delete(self, key):
    os.unlink(self.k2p(key))


  def get(self, key):
    return open(self.k2p(key), "rb")


  def put(self, key, value):
    # TODO: refactor to use a tempfile and symlink
    with open(self.k2p(key, True), "wb") as f:
      f.write(value)


if os.environ['TYPE'] == "volume":
  host = socket.gethostname()

  fc = FileCache(os.environ['VOLUME'])

def volume(env, sr):
  key = env['REQUEST_URI'].encode('utf-8')
  hkey = hashlib.md5(key).hexdigest()
  print(hkey)

  if env['REQUEST_METHOD'] == 'PUT':
    flen = int(env.get('CONTENT_LENGTH', '0'))
    if flen > 0:
      fc.put(hkey, env['wsgi.input'].read(flen))
      return resp(sr, '201 Created')
    else:
      return resp(sr, '411 Length Required')

  if not fc.exists(hkey):
    # key not in fc
    return resp(sr, '404 Not Found')            # key does not exist

  if env['REQUEST_METHOD'] == 'GET':
    return resp(sr, '200 OK', body=fc.get(hkey).read())

  if env['REQUEST_METHOD'] == 'DELETE':
    fc.delete(hkey)
    return resp(sr, '200 OK')

