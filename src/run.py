def master(env,start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [b'Hello World']

def volume(env,start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [b'Nope']


# def application(environ, start_response):
#     status = '200 OK'
#     output = 'Hello World!\n'
#     response_headers = [('Content-type', 'text/plain'),
#                         ('Content-Length', str(len(output)))]
#     start_response(status, response_headers)
#     return [output]
