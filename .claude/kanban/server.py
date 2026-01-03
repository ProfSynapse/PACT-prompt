#!/usr/bin/env python3
"""
Lightweight kanban server - serves board.html and provides transcript API.

Usage:
    python3 server.py [port]

Default port: 8420
"""

import http.server
import json
import os
import sys
import urllib.parse
from pathlib import Path

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8420
KANBAN_DIR = Path(__file__).parent


class KanbanHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(KANBAN_DIR), **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        # API: Get transcript content
        if parsed.path == '/api/transcript':
            query = urllib.parse.parse_qs(parsed.query)
            transcript_path = query.get('path', [''])[0]

            if not transcript_path:
                self.send_error(400, "Missing 'path' parameter")
                return

            # Security: only allow reading .jsonl files from .claude directories
            if not transcript_path.endswith('.jsonl') or '..' in transcript_path:
                self.send_error(403, "Invalid transcript path")
                return

            try:
                with open(transcript_path, 'r') as f:
                    content = f.read()

                # Parse JSONL and extract assistant messages
                messages = []
                for line in content.strip().split('\n'):
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        # Extract relevant info from transcript
                        if entry.get('type') == 'assistant':
                            msg = entry.get('message', {})
                            content_parts = msg.get('content', [])
                            for part in content_parts:
                                if isinstance(part, dict) and part.get('type') == 'text':
                                    messages.append({
                                        'type': 'text',
                                        'content': part.get('text', '')
                                    })
                                elif isinstance(part, dict) and part.get('type') == 'tool_use':
                                    messages.append({
                                        'type': 'tool',
                                        'tool': part.get('name', 'unknown'),
                                        'input': str(part.get('input', ''))[:200]
                                    })
                    except json.JSONDecodeError:
                        continue

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'path': transcript_path,
                    'messages': messages,
                    'raw_lines': len(content.strip().split('\n'))
                }).encode())

            except FileNotFoundError:
                self.send_error(404, f"Transcript not found: {transcript_path}")
            except Exception as e:
                self.send_error(500, str(e))
            return

        # Default: serve static files
        super().do_GET()

    def log_message(self, format, *args):
        # Quieter logging
        if '/api/' in args[0] or args[0].endswith('.html'):
            print(f"[kanban] {args[0]}")


def main():
    print(f"🛠️ PACT Kanban Server")
    print(f"   Board:  http://localhost:{PORT}/board.html")
    print(f"   API:    http://localhost:{PORT}/api/transcript?path=...")
    print(f"   Press Ctrl+C to stop\n")

    with http.server.HTTPServer(('', PORT), KanbanHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down...")


if __name__ == '__main__':
    main()
