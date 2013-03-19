#!/usr/bin/python
# -*- coding: utf-8 -*-

import cgi
import argparse
from random import randint
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from multiprocessing import Value

parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, default=65123)
parser.add_argument("--stream-url", dest="stream_url", help="Stream url", required = True)
parser.add_argument("--test-url", dest="test_url", help="Testing stream url", required = True)

options = parser.parse_args()

#This class will handles any incoming request from
#the browser
class Handler(BaseHTTPRequestHandler):
    started = Value('b', False)
    started_test = Value('b', False)

    index = """
<html>
<body>
<video controls>
    <source src="STREAM_URL" type='video/webm'/>
    <source src="TEST_URL" type='video/webm'/>
</video>
<img src="/slide"></img>
<br/>
STREAM_START_STOP
TEST_START_STOP
</body>
</html>"""

    #Handler for the GET requests
    def do_GET(self):
        index = self.index.replace("STREAM_URL", options.stream_url + "?nocache=%d" %randint(1,9999))
        index = index.replace("TEST_URL", options.test_url + "?nocache=%d" %randint(1,9999))
        if self.path=="/":
            mimetype='text/html'

            self.send_response(200)
            self.send_header('Content-type', mimetype)
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()

            replacement = ("""<a href="/stop">Stop stream</a>"""
                            if self.started.value else
                           """<a href="/start">Start stream</a>""")
            index = index.replace("STREAM_START_STOP", replacement)

            replacement = ("""<a href="/stop_test">Stop test stream</a>"""
                            if self.started_test.value else
                           """<a href="/start_test">Start test stream</a>""")
            self.wfile.write(index.replace("TEST_START_STOP", replacement))

            return

        elif self.path=="/start":
            mimetype='text/html'

            self.started.value = True

            self.send_response(301)
            self.send_header('Location','/')

        elif self.path=="/stop":
            mimetype='text/html'

            self.started.value = False

            self.send_response(301)
            self.send_header('Location','/')

        elif self.path=="/start_test":
            mimetype='text/html'

            self.started_test.value = True

            self.send_response(301)
            self.send_header('Location','/')

        elif self.path=="/stop_test":
            mimetype='text/html'

            self.started_test.value = False

            self.send_response(301)
            self.send_header('Location','/')

        elif self.path=="/started":
            mimetype='text/html'

            self.send_response(200)
            self.send_header('Content-type', mimetype)
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()

            self.wfile.write("True" if self.started.value else "False")

            return

        elif self.path=="/started_test":
            mimetype='text/html'

            self.send_response(200)
            self.send_header('Content-type', mimetype)
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()

            self.wfile.write("True" if self.started_test.value else "False")

            return

        elif self.path=="/slide":
            try: fd = open('.slide', "rb")
            except IOError:
                self.send_error(404,'Slide Not Found!')
                return

            mimetype = 'image/jpg'

            self.send_response(200)
            self.send_header('Content-type', mimetype)
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()

            self.wfile.write(fd.read())
            fd.close()

            return

        self.send_header("Cache-Control", "no-cache")
        self.end_headers()

    def do_POST(self):
        form = cgi.FieldStorage(fp=self.rfile, headers=self.headers,
                                environ = {'REQUEST_METHOD':'POST',
                                           'CONTENT_TYPE': self.headers['Content-Type'],
                                          }
                               )
        upfile = form['slide']

        fd = open(".slide", "wb")
        fd.write(upfile.file.read())
        fd.close()

        self.send_response(301)
        self.send_header('Location','/')
        self.end_headers()
try:
	#Create a web server and define the handler to manage the
	#incoming request
	server = HTTPServer(('', options.port), Handler)
	print 'Started httpserver on port ' , options.port

	#Wait forever for incoming htto requests
	server.serve_forever()

except KeyboardInterrupt:
	print '^C received, shutting down the web server'
	server.socket.close()
