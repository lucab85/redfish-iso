#!/usr/bin/env python3
"""
Robust HTTP server for serving ISOs to iDRAC
Usage: python3 robust_http_server.py /path/to/iso/directory
"""
import sys
import socketserver
from http.server import SimpleHTTPRequestHandler
from functools import partial
import os

class RobustHTTPRequestHandler(SimpleHTTPRequestHandler):
    """HTTP handler with longer timeouts and better error handling"""
    
    protocol_version = "HTTP/1.1"  # Enable keep-alive
    
    def log_message(self, format, *args):
        """Add more detailed logging"""
        sys.stderr.write("%s - - [%s] %s\n" %
                         (self.address_string(),
                          self.log_date_time_string(),
                          format % args))
    
    def end_headers(self):
        """Add headers to prevent timeout"""
        # Disable buffering for large files
        self.send_header('Connection', 'keep-alive')
        self.send_header('Keep-Alive', 'timeout=300, max=100')
        SimpleHTTPRequestHandler.end_headers(self)

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """Handle requests in separate threads"""
    allow_reuse_address = True
    daemon_threads = True
    request_queue_size = 10
    
    # Increase socket timeout for large file transfers
    timeout = 600  # 10 minutes

def main():
    port = 8000
    directory = sys.argv[1] if len(sys.argv) > 1 else '.'
    
    os.chdir(directory)
    
    handler = partial(RobustHTTPRequestHandler)
    
    with ThreadedTCPServer(("0.0.0.0", port), handler) as httpd:
        print(f"Serving files from: {os.getcwd()}")
        print(f"HTTP server running on http://0.0.0.0:{port}/")
        print("Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down...")
            httpd.shutdown()

if __name__ == "__main__":
    main()