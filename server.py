"""
server.py - The main program for running a web interface in this project
Copyright EJM Software 2016

Usage: python server.py
"""
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import cgi, pickle, os, generator, waveform, base64, StringIO

PORT_NUMBER = 8080

class StoreHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        print "POST REQUEST"
        try:
            # Get the form data
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD':'POST',
                         'CONTENT_TYPE':self.headers['Content-Type'],
                         })
            # create a new generator object
            g = generator.Generator()
            # load pickle data into the generator
            if os.path.exists("pattern-data.pickle"):
                g.pattern_dictionary = pickle.load(open("pattern-data.pickle", "rb" ))
            # Add the submitted file to the generator's knowledge base
            g.add_wave(form['file'].file)
            # dump the data into a pickle file
            pickle.dump(g.pattern_dictionary, open("pattern-data.pickle", "wb"))
            # Build an output song
            output = StringIO.StringIO()
            waveform.to_file(output, waveform.from_string(str(g.run())))
            # Send header
            self.send_response(200)
            self.send_header("Content-type", "application/octet-stream")
            self.end_headers()
            self.wfile.write(base64.b64encode(output.read()))
            # Send body, encoded in base64
            #f = open("test1234.wav", 'rb')
        except:
            pass

    def do_GET(self):
        response = open("webapp.html", "r").read()
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-length", len(response))
        self.end_headers()
        self.wfile.write(response)

try:
    # create a web server and define the handler to manage the incoming request
    server = HTTPServer(('', PORT_NUMBER), StoreHandler)
    print 'Started httpserver on port' , PORT_NUMBER
    # wait forever for incoming http requests
    server.serve_forever()
except KeyboardInterrupt:
    print '^C received, shutting down the web server'
    server.socket.close()
