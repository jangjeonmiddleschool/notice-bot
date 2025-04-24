from flask import Flask, request, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)

# Google Drive API 인증 설정
SERVICE_ACCOUNT_FILE = 'credentials.json'  # 서비스 계정 키 JSON 파일 경로
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
FOLDER_ID = '1L-zGDaoyRvkq8KsV9lc5yznxSXVuQayx'  # 공유 폴더 ID

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)

# 파일 목록 가져오기 함수
def get_notice_files():
    results = drive_service.files().list(
        q=f"'{FOLDER_ID}' in parents and trashed = false",
        fields="files(id, name)",
        orderBy="name desc"
    ).execute()
    files = results.get('files', [])
    return files

# 카카오 챗봇 웹훅 엔드포인트
@app.route("/notices", methods=["POST"])
def notice_list():
    files = get_notice_files()
    buttons = []
    for file in files[:5]:  # 최대 5개까지 버튼
        label = file['name'].replace('_', ' ').split('.')[0]
        url = f"https://drive.google.com/uc?export=view&id={file['id']}"
        buttons.append({
            "action": "webLink",
            "label": label,
            "webLinkUrl": url
        })

    response = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "basicCard": {
                        "title": "📎 가정통신문 목록",
                        "description": "선택하신 것을 누르세요",
                        "buttons": buttons
                    }
                }
            ]
        }
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
