import http.server
import json
import os

# 통신 포트 (80번 포트를 사용하여 주소창에 IP만 쳐도 들어오게 세팅)
PORT = 80
DATA_FILE = "data.json"

# 초기 파일이 없을 경우 공용 JSON 템플릿 생성
if not os.path.exists(DATA_FILE):
    default_structure = {
        "policyData": [],
        "lunchMenus": ["김치찌개", "돈까스", "제육볶음", "짜장면", "초밥", "햄버거", "마라탕", "쌀국수"],
        "memo": ""
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(default_structure, f, ensure_ascii=False, indent=2)

class CompanyDataServer(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # 브라우저가 접속 시 최신 데이터를 달라고 할 때 처리
        if self.path == '/api/data':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            # 다른 PC에서 간혹 발생하는 캐시 꼬임 방지
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
            self.end_headers()
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.wfile.write(f.read().encode('utf-8'))
        else:
            # 그 외 기본 접속은 원래대로 폴더 내 HTML 파일을 매핑하여 보여줌
            super().do_GET()

    def do_POST(self):
        # 목록을 변경하거나 메모를 입력하여 서버에 저장할 때 처리
        if self.path == '/api/data':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                # 받은 원격 데이터를 그대로 data.json 파일에 안전하게 오버라이트
                updated_json = json.loads(post_data.decode('utf-8'))
                with open(DATA_FILE, "w", encoding="utf-8") as f:
                    json.dump(updated_json, f, ensure_ascii=False, indent=2)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"status": "success"}')
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f'{"error": "{str(e)}"}'.encode())

server = http.server.HTTPServer(('0.0.0.0', PORT), CompanyDataServer)
server.serve_forever()