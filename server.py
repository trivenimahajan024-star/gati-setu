import http.server
import socketserver
import os
import sys
import webbrowser

PORT = 8000
DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        # Enable CORS and caching headers for smooth dev experience
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()

if __name__ == "__main__":
    os.chdir(DIRECTORY)
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        url = f"http://127.0.0.1:{PORT}"
        print("==================================================================")
        print("  [GatiSetu] - Dynamic ETA & Railway Operations Platform")
        print(f"  Serving Unified Application at: {url}")
        print("  Press Ctrl+C to stop the server.")
        print("==================================================================")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down GatiSetu server.")
            httpd.server_close()
