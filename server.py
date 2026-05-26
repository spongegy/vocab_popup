"""
어휘 도우미 리더 - 백엔드 서버
로컬: python server.py
Render: 자동 실행
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.request
import urllib.parse
import os

API_KEY = os.environ.get("KRDICT_KEY", "")

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api/dict"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            word = params.get("q", [""])[0]
            if not word or not API_KEY:
                self._respond(400, b"missing query or key", "text/plain")
                return
            # advanced 옵션 제거, num=10으로 단순화
            api_url = (
                f"https://krdict.korean.go.kr/api/search"
                f"?key={API_KEY}"
                f"&q={urllib.parse.quote(word)}"
                f"&sort=popular&start=1&num=10"
            )
            try:
                req = urllib.request.Request(
                    api_url,
                    headers={
                        "User-Agent": "Mozilla/5.0",
                        "Accept": "application/xml, text/xml, */*",
                    }
                )
                with urllib.request.urlopen(req, timeout=10) as r:
                    data = r.read()
                self._respond(200, data, "application/xml; charset=utf-8")
            except Exception as e:
                self._respond(500, str(e).encode(), "text/plain")
            return
        super().do_GET()

    def _respond(self, code, body, ctype):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print(f"[server] {fmt % args}")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    port = int(os.environ.get("PORT", 5000))
    print(f"✅ 서버 시작 → http://localhost:{port}")
    HTTPServer(("", port), Handler).serve_forever()
