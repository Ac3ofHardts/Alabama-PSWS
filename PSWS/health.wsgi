import sys
def application(environ, start_response):
    start_response('200 OK', [('Content-Type','text/plain')])
    return [("OK py=" + sys.version + "\n").encode()]
