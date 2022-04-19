import os
import time
import json
import random
import socket
import hashlib
import tempfile
import xattr

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

  if env['REQUEST_METHOD'] == 'POST':
    flen = int(env.get('CONTENT_LENGTH', '0'))
    if flen > 0:
    # POST is called by the volume servers to write to the database
      db.put(key.encode('utf-8'), env['wsgi.input'].read(), sync=True)
    else:
      db.delete(key.encode('utf-8'))
    return resp(sr, '200 OK')


  metakey = db.get(key.encode('utf-8'))

  if metakey is None:
    if env['REQUEST_METHOD'] == 'PUT':
      # TODO: make volume selection intelligent
      volume = random.choice(volumes)
    else:
      # this key doesn't exist and we aren't trying to create it
      return resp(sr, '404 Not Found')
  else:
    # key found
    if env['REQUEST_METHOD'] == 'PUT':
      return resp(sr, '409 Conflict')
    meta = json.loads(metakey.decode('utf-8'))
    volume = meta['volume']


  # send redirect
  headers = [('Location', 'http://%s%s' % (volume, key))]

  return resp(sr, '307 Temporary Redirect', headers)


# --- Volume Server ---
class FileCache(object):
  # single computer on disk key value store
  def __init__(self, basedir):
    self.basedir = os.path.realpath(basedir)
    self.tmpdir = os.path.join(self.basedir, "tmp")      # create temp file
    os.makedirs(self.tmpdir, exist_ok=True)
    print("FileCache in %s" % basedir)


  def k2p(self, key, mkdir_ok=False):
    key = hashlib.md5(key).hexdigest()

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


  def put(self, key, stream, fullname=None):
    with tempfile.NamedTemporaryFile(dir=self.tmpdir, delete=False) as f:       # might not be cleaned up due to delete
      # chunks, don't waste RAM
      f.write(stream.read())

      # save real name in xattr in case we rebuild it
      xattr.setxattr(f.name, 'user.key', key)

      # check hash here
      os.rename(f.name, self.k2p(key, True))

if os.environ['TYPE'] == "volume":
  host = socket.gethostname()

  fc = FileCache(os.environ['VOLUME'])

def volume(env, sr):
  key = env['REQUEST_URI'].encode('utf-8')
  print(key)

  if env['REQUEST_METHOD'] == 'PUT':
    if fc.exists(key):
      # can't write already exists
      return resp(sr, '409 Conflict')

    flen = int(env.get('CONTENT_LENGTH', '0'))
    if flen > 0:
      fc.put(key, env['wsgi.input'])
      # notify database with hostname and operating port

      return resp(sr, '201 Created')
    else:
      return resp(sr, '411 Length Required')

  if not fc.exists(key):
    # key not in fc
    return resp(sr, '404 Not Found')            # key does not exist

  if env['REQUEST_METHOD'] == 'GET':
    # chunks, don't waste RAM
    return resp(sr, '200 OK', body=fc.get(key).read())

  if env['REQUEST_METHOD'] == 'DELETE':
    fc.delete(key)
    return resp(sr, '200 OK')

