import os
import time
import json
import random
import socket
import hashlib
import tempfile

print("hello", os.environ['TYPE'], os.getpid())    # hello environment variable and process id


def resp(sr, code, headers=[('Content-type', 'text/plain')], body=b''):
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
    self.tmpdir = os.path.join(self.basedir, "tmp")      # create temp file
    os.makedirs(self.tmpdir, exist_ok=True)
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


  def put(self, key, stream):
    with tempfile.NamedTemporaryFile(dir=self.tmpdir, delete=False) as f:       # might not be cleaned up due to delete
      # chunks, don't waste RAM
      f.write(stream.read())
      os.rename(f.name, self.k2p(key, True))

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
      fc.put(hkey, env['wsgi.input'])
      return resp(sr, '201 Created')
    else:
      return resp(sr, '411 Length Required')

  if not fc.exists(hkey):
    # key not in fc
    return resp(sr, '404 Not Found')            # key does not exist

  if env['REQUEST_METHOD'] == 'GET':
    # chunks, don't waste RAM
    return resp(sr, '200 OK', body=fc.get(hkey).read())

  if env['REQUEST_METHOD'] == 'DELETE':
    fc.delete(hkey)
    return resp(sr, '200 OK')

