__author__ = 'Jaakko Aro'

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from monitor_app import NoResponse
import logging

PORT = 8080
logger = logging.getLogger('web_monitor')


RESPONSE_TEMPLATE = """\
<head>
<title>Web Monitor Statuspage</title>
<style media="screen" type="text/css">
div {
    border: 1px solid;
    width: 200px;
    height: 200px;
    float: left;
}
div.success {
    background-color: lightgreen;
}
div.warning {
    background-color: #FFFF66;
}
div.error {
    background-color: lightcoral;
}
</style>
</head>
<body>
%s
</body>
"""

STATUS_TEMPLATE = """\
<div class="%(class)s">
<h1><a href="%(url)s">%(page_name)s</a></h1>
<p>Response Time : %(response_time).2fs</p>
<p>Content: %(content_status)s</p>
</div>
"""

ERROR_TEMPLATE = """\
<div class="error">
<h1><a href="%s">%s</a></h1>
<h2>NOT RESPONDING</h2>
</div>
"""


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        content = list()
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        for page in sorted(self.server.monitored_pages):
            try:
                if page.get_status():
                    content.append(STATUS_TEMPLATE % {'class': 'success', 'page_name': page.name,
                                                      'response_time': page.get_response_time(),
                                                      'content_status': 'OK',
                                                      'url': page.url})
                else:
                    content.append(STATUS_TEMPLATE % {'class': 'warning', 'page_name': page.name,
                                                      'response_time': page.get_response_time(),
                                                      'content_status': 'OK' if page.contains_required_string()
                                                      else 'NOK',
                                                      'url': page.url})

            except NoResponse:
                content.append(ERROR_TEMPLATE % (page.url, page.name))
        self.wfile.write(RESPONSE_TEMPLATE % '\n'.join(content))

    def log_message(self, format, *args):
        logger.info(format % args)

    def log_error(self, format, *args):
        logger.error(format % args)


class VerySimpleHttpServer(HTTPServer):
    def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True, monitored_pages=list()):
        self.monitored_pages = monitored_pages
        HTTPServer.__init__(self, server_address, RequestHandlerClass, bind_and_activate)  # BaseServer is old style
                                                                                           # class so need to use old
                                                                                           # style super


def run_server(monitored_pages):
    server = VerySimpleHttpServer(('0.0.0.0', PORT), RequestHandler, monitored_pages=monitored_pages)
    logger.info('HTTP Server started')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()

