import os
import time
import json
import xattr
import random
import socket
import hashlib
import tempfile
import requests


# Path variables:
# QUERY_STRING

# --- Global ---
print("hello", os.environ['TYPE'], os.getpid())    # hello file name process id

def resp(start_response, code, headers=[('Content-type', 'text/plain')], body=b''):
  start_response(code, headers)
  return [body]

# --- Master Server --
if os.environ['TYPE'] == "master":
  # check on volume servers
  volumes = os.environ['VOLUMES'].split(",")

  # for v in volumes:
  #   print(v)

  import plyvel
  db = plyvel.DB(os.environ['DB'], create_if_missing=True)     # create plyvel database

def master(env, sr):
  host = env['SERVER_NAME'] + ":" + env['SERVER_PORT']        # host adress
  key = env['PATH_INFO']

  if env['REQUEST_METHOD'] == 'POST':
    # POST called by volume servers to write to DB
    flen = int(env.get('CONTENT_LENGTH', '0'))
    print("posting", key, flen)

    if flen > 0:
      db.put(key.encode('utf-8'), env['wsgi.input'].read())     # put the key value in the db
    else:
      db.delete(key.encode('utf-8'))
    return resp(sr, '200 OK')

  metakey = db.get(key.encode('utf-8'))
  print(key, metakey)

  if metakey is None:
    if env['REQUEST_METHOD'] == 'PUT':
      # TODO: make volume selection intelligent
      # handle putting
      volume = random.choice(volumes)
    else:
      # doesnt exist and we are not trying to create it
      return resp(sr, '404 Not Found')
  else:
    # key found
    if env['REQUEST_METHOD'] == 'PUT':
      return resp(sr, '409 Conflict')

    meta = json.loads(metakey.decode('utf-8'))
    volume = meta['volume']

  # redirect
  headers = [('Location', 'http://%s%s?%s' % (volume, key, host))]

  return resp(sr, '307 Temporary Redirect', headers)


# --- Volume Server ---
class FileCache(object):
  # this is a single computer on disk key value store

  def __init__(self, basedir):
    self.basedir = os.path.realpath(basedir)            # base directory
    self.tmpdir = os.path.join(self.basedir, "tmp")     # temporary directory
    os.makedirs(self.tmpdir, exist_ok=True)             # create the directories

    print("FileCache in %s" % basedir)

  def k2p(self, key, mkdir_ok=False):
    key = hashlib.md5(key.encode('utf-8')).hexdigest()

    path = self.basedir + "/" + key[0:2] + "/" + key[0:4]

    if not os.path.isdir(path) and mkdir_ok:
      os.makedirs(path, exist_ok=True)

    return os.path.join(path, key)

  def exists(self, key):
    return os.path.isfile(self.k2p(key))

  def delete(self, key):
    try:
      os.unlink(self.k2p(key))
      return True
    except FileNotFoundError:
      pass
    return False

  def get(self, key):
    return open(self.k2p(key), "rb")

  def put(self, key, stream):
    with tempfile.NamedTemporaryFile(dir=self.tmpdir, delete=False) as f:
      # chunks, don't waste RAM
      f.write(stream.read())

      # save the real name in xattr in case we rebuild cache
      xattr.setxattr(f.name, 'user.key', key.encode('utf-8'))

      # TODO: check hash
      os.rename(f.name, self.k2p(key, True))

if os.environ['TYPE'] == "volume":
  # create the FC
  fc = FileCache(os.environ['VOLUME'])

def volume(env, sr):
  host = env['SERVER_NAME'] + ":" + env['SERVER_PORT']         # host adress
  key = env['PATH_INFO']

  if env['REQUEST_METHOD'] == 'PUT':
    if fc.exists(key):
      req = requests.post("http://" + env['QUERY_STRING'] + key, json={"volume": host})
      # can't write, already exists
      return resp(sr, '409 Conflict')

    flen = int(env.get('CONTENT_LENGTH', '0'))
    if flen > 0:
      fc.put(key, env['wsgi.input'])

      req = requests.post("http://"+env['QUERY_STRING']+key, json={"volume": host})

      if req.status_code == 200:
        return resp(sr, '201 Created')
      else:
        fc.delete(key)
        return resp(sr, '500 Internal Server Error')
    else:
      return resp(sr, '411 Length Required')

  if env['REQUEST_METHOD'] == 'DELETE':
    req = requests.post("http://" + env['QUERY_STRING'] + key, data='')

    if req.status_code == 200:
      if fc.delete(key):
        return resp(sr, '200 OK')
      else:
        # file wasn't on our disk
        return resp(sr, '500 Internal Server Error (not on disk)')
    else:
      return resp(sr, '500 Internal Server Error (master db write fail)')

  if not fc.exists(key):
    # 404, key not in FC
    return resp(sr, '404 Not Found')

  if env['REQUEST_METHOD'] == 'GET':
    # chunks, don't waste RAM
    return resp(sr, '200 OK', body=fc.get(key).read())
