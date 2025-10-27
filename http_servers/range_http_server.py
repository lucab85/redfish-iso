#!/usr/bin/env python3
"""
HTTP server with Range request support for iDRAC ISO mounting
Usage: python3 range_http_server.py [port] [directory]
"""
import os
import sys
import socketserver
from http.server import SimpleHTTPRequestHandler
from functools import partial
import mimetypes

class RangeHTTPRequestHandler(SimpleHTTPRequestHandler):
    """HTTP handler with Range request support"""
    
    protocol_version = "HTTP/1.1"
    
    def do_GET(self):
        """Serve GET request with range support"""
        path = self.translate_path(self.path)
        
        if not os.path.exists(path):
            self.send_error(404, "File not found")
            return
        
        if os.path.isdir(path):
            return SimpleHTTPRequestHandler.do_GET(self)
        
        # Get file stats
        try:
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return
        
        fs = os.fstat(f.fileno())
        file_len = fs.st_size
        
        # Check for Range header
        range_header = self.headers.get('Range')
        
        if range_header:
            # Parse range
            try:
                range_val = range_header.split('=')[1]
                start, end = range_val.split('-')
                start = int(start) if start else 0
                end = int(end) if end else file_len - 1
                
                if start >= file_len:
                    self.send_error(416, "Requested Range Not Satisfiable")
                    f.close()
                    return
                
                # Send partial content
                self.send_response(206)
                self.send_header("Content-Type", self.guess_type(path))
                self.send_header("Content-Range", f"bytes {start}-{end}/{file_len}")
                self.send_header("Content-Length", str(end - start + 1))
                self.send_header("Accept-Ranges", "bytes")
                self.send_header("Connection", "keep-alive")
                self.end_headers()
                
                f.seek(start)
                chunk_size = 8192
                bytes_to_send = end - start + 1
                
                while bytes_to_send > 0:
                    chunk = f.read(min(chunk_size, bytes_to_send))
                    if not chunk:
                        break
                    try:
                        self.wfile.write(chunk)
                        bytes_to_send -= len(chunk)
                    except (BrokenPipeError, ConnectionResetError):
                        print(f"Connection reset by client during range request")
                        break
                
                f.close()
                return
                
            except Exception as e:
                print(f"Range request error: {e}")
                f.close()
                self.send_error(400, "Bad Range Request")
                return
        
        # Normal full file response
        self.send_response(200)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Content-Length", str(file_len))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        
        # Send file in chunks with error handling
        chunk_size = 65536  # 64KB chunks
        try:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                self.wfile.write(chunk)
        except (BrokenPipeError, ConnectionResetError) as e:
            print(f"Connection reset by client: {e}")
        finally:
            f.close()
    
    def do_HEAD(self):
        """Serve HEAD request"""
        path = self.translate_path(self.path)
        
        if not os.path.exists(path) or os.path.isdir(path):
            return SimpleHTTPRequestHandler.do_HEAD(self)
        
        try:
            f = open(path, 'rb')
            fs = os.fstat(f.fileno())
            f.close()
            
            self.send_response(200)
            self.send_header("Content-Type", self.guess_type(path))
            self.send_header("Content-Length", str(fs.st_size))
            self.send_header("Accept-Ranges", "bytes")
            self.end_headers()
        except IOError:
            self.send_error(404, "File not found")

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True
    timeout = 600

def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    directory = sys.argv[2] if len(sys.argv) > 2 else '.'
    
    os.chdir(directory)
    
    handler = partial(RangeHTTPRequestHandler)
    
    with ThreadedTCPServer(("0.0.0.0", port), handler) as httpd:
        print(f"Serving files from: {os.getcwd()}")
        print(f"HTTP server with Range support on http://0.0.0.0:{port}/")
        print("Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down...")

if __name__ == "__main__":
    main()