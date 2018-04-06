"""
server.py - The main program for running a web interface in this project
:author: Elliot Miller

Usage: python server.py
"""
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import cgi, pickle, os, generator, waveform, base64, StringIO, sys

PORT_NUMBER = 8080

class StoreHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """All post requests are sent using AJAX from the web app. The requests
        should contain one waveform file to be parsed and added to the pattern
        dictionary. After the file is parsed, an output wavform will be sent."""
        try:
            # get the form data
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
            # if the user submitted a file, add it to the generator's dictionary
            f = form['file'].file
            f.seek(0, 2)
            if f.tell() > 0:
                print "Success: A valid input file was received."
                f.seek(0,0)
                g.add_wave(f)
            else:
                print "Warning: No valid file was received."
            # dump the data into a pickle file
            pickle.dump(g.pattern_dictionary, open("pattern-data.pickle", "wb"))
            # build an output song
            print "Loaded Pattern Dictionary. Generating Song"
            output = StringIO.StringIO()
            waveform.to_file(output, waveform.from_string(str(g.run())))
            print "Song Finished"
            # send header and body encoded in base64, which is what the web app
            # is using
            self.send_response(200)
            self.send_header("Content-type", "application/octet-stream")
            self.end_headers()
            self.wfile.write(base64.b64encode(output.getvalue()))
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def do_GET(self):
        """Send the html web app to the client"""
        response = open("webapp.html", "r").read()
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-length", len(response))
        self.end_headers()
        self.wfile.write(response)

if __name__=="__main__":
    try:
        # create a web server and define the handler to manage the incoming request
        server = HTTPServer(('', PORT_NUMBER), StoreHandler)
        print 'Started httpserver on port' , PORT_NUMBER
        # wait forever for incoming http requests
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down the web server'
        server.socket.close()
