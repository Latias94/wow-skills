"""Serve the buildless trainer with a correct module MIME type on Windows."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

class TrainerHandler(SimpleHTTPRequestHandler):
    def guess_type(self, path):
        if path.lower().endswith('.mjs'):
            return 'text/javascript'
        return super().guess_type(path)


root = Path(__file__).resolve().parents[1] / 'dist'
handler = partial(TrainerHandler, directory=str(root))
print('Windwalker trainer: http://127.0.0.1:8766', flush=True)
ThreadingHTTPServer(('127.0.0.1', 8766), handler).serve_forever()
