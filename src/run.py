import os
import sys

print("Hello", sys.argv, os.environ['TYPE'])

def master(env,start_response):
    print(os.getpid())
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [b'Hello World']

def volume(env,start_response):
    print(os.getpid())
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [b'Nope world']
