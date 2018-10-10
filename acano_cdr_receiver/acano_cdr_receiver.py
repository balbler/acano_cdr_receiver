from http.server import BaseHTTPRequestHandler, HTTPServer
import getopt
import sys
import os
import datetime

log_file = ""


class S(BaseHTTPRequestHandler):

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self.wfile.write("<html><body><h1>hello</h1></body></html>")

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        """
        Handles POST request from the Acano Call Bridge and parses the CDR data into the parser function
        :return:
        """
        self._set_headers()
        # For future use, self.path contains the URL path in the request, e.g. /MyServer
        content_len = int(self.headers.get('content-length', 0))
        post_body = self.rfile.read(content_len)
        #content = xmltodict.parse(post_body.decode('utf-8'))

        self.write_to_disk(post_body, log_file)


    

    @staticmethod
    def write_to_disk(json_output, dest_file):
        """
        Accepts in the parsed JSON CDR data and write it to disk
        If the destination file reaches 100MB in size it will be renamed with a timestamp suffix
        and future logs will be written to a new copy of the requested destination file
        :param json_output:
        :param dest_file:
        :return:
        """

        if os.path.isfile(dest_file):
            statinfo = os.stat(dest_file)
            if statinfo.st_size > 100000000:  # 100 MB
                rotate_dest = dest_file + "." + str(datetime.datetime.utcnow().strftime('%Y_%m_%dT%H_%M_%S'))
                os.rename(dest_file, rotate_dest)

        file = open(dest_file, 'a')
        file.write(json_output)
        file.write("\n\n")
        file.close()


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "f:", ["--file="])
    except getopt.GetoptError:
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-f', '--file'):
            global log_file
            log_file = arg
            server_address = ('', 9999)
            httpd = HTTPServer(server_address, S)
            print("Starting httpd")
            httpd.serve_forever()

if __name__ == "__main__":
    main(sys.argv[1:])
