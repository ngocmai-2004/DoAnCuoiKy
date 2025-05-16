import os
import json
import csv
import requests
from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)
app.secret_key = "your-secret-key"  # Thay bằng key bảo mật thực tế
data_directory = 'data/'
users_file = 'D:\\bank_proj\\user.json'
feedback_file = 'D:\\bank_proj\\feedback.json'  # File lưu phản hồi

API_KEY = "AIzaSyDe4ZTpmEQSATWA6gawvxkQ6_ah9q3pAs8"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

# Hàm đọc file JSON
def read_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"❗ Lỗi khi đọc file {file_path}: {str(e)}")
        return None

# Hàm ghi file JSON
def write_json(file_path, data):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❗ Lỗi khi ghi file {file_path}: {str(e)}")
        return False

# Hàm xác thực người dùng
def authenticate_user(username, password):
    users = read_json(users_file)
    if not users:
        return None
    for user in users:
        if user['username'] == username and user['password'] == password:
            return user
    return None

# Hàm kiểm tra quyền truy cập file
def has_permission(user, file_name):
    if file_name in user['permissions']:
        return True
    return False

def ask_gemini(message):
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": message}]
            }
        ]
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        try:
            return data['candidates'][0]['content']['parts'][0]['text']
        except (KeyError, IndexError):
            return "❗ Error from AI."
    else:
        return f"❌ Error: {response.status_code} - {response.text}"

def read_txt(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        return f"❗ Error when reading file {file_path}: {str(e)}"

def read_json_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        return f"❗ Error when reading file {file_path}: {str(e)}"

def read_csv(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            data = "\n".join([", ".join(row) for row in reader])
            return data
    except Exception as e:
        return f"❗ Error when reading file {file_path}: {str(e)}"

def process_data_files(directory):
    file_data = {}
    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        if os.path.isfile(file_path):
            ext = file_name.split('.')[-1].lower()
            if ext == 'txt':
                content = read_txt(file_path)
            elif ext == 'json':
                content = read_json_data(file_path)
            elif ext == 'csv':
                content = read_csv(file_path)
            else:
                content = f"❗ Error when reading file {ext}."
            file_data[file_name] = content
    return file_data

file_data = process_data_files(data_directory)

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    user = authenticate_user(username, password)
    if user:
        session["username"] = username
        session["permissions"] = user["permissions"]
        return jsonify({"success": True, "permissions": user["permissions"]})
    return jsonify({"success": False, "message": "Sai tên đăng nhập hoặc mật khẩu."}), 401

@app.route("/api/logout", methods=["POST"])
def logout():
    session.pop("username", None)
    session.pop("permissions", None)
    return jsonify({"success": True})

@app.route("/api/files")
def get_files():
    if "username" not in session:
        return jsonify({"error": "Chưa đăng nhập."}), 401
    permissions = session.get("permissions", [])
    allowed_files = [f for f in file_data.keys() if f in permissions]
    return jsonify(allowed_files)

@app.route("/api/file-content")
def get_file_content():
    if "username" not in session:
        return jsonify({"error": "Chưa đăng nhập."}), 401
    file = request.args.get('file')
    if file not in session.get("permissions", []):
        return jsonify({"error": "Không có quyền truy cập file này."}), 403
    content = file_data.get(file, "")
    if isinstance(content, str):
        return jsonify({"content": content[:1000]})
    else:
        return jsonify({"content": json.dumps(content, ensure_ascii=False)[:1000]})

@app.route("/api/ask", methods=["POST"])
def ask_question():
    if "username" not in session:
        return jsonify({"error": "Chưa đăng nhập."}), 401
    data_input = request.get_json()
    file = data_input.get("file")
    question = data_input.get("question")
    if file not in session.get("permissions", []):
        return jsonify({"error": "Không có quyền truy cập file này."}), 403
    content = file_data.get(file, "")
    if isinstance(content, dict):
        content = json.dumps(content, ensure_ascii=False)
    prompt = f"{content}\nQuestion: {question}"
    response = ask_gemini(prompt)
    return jsonify({"answer": response})

@app.route("/api/feedback", methods=["POST"])
def save_feedback():
    if "username" not in session:
        return jsonify({"error": "Chưa đăng nhập."}), 401
    data = request.get_json()
    file = data.get("file")
    question = data.get("question")
    answer = data.get("answer")
    feedback = data.get("feedback")  # "like" hoặc "dislike"
    
    if file not in session.get("permissions", []):
        return jsonify({"error": "Không có quyền truy cập file này."}), 403
    
    # Đọc file feedback.json
    feedback_data = read_json(feedback_file) or []
    
    # Thêm phản hồi mới
    feedback_entry = {
        "username": session["username"],
        "file": file,
        "question": question,
        "answer": answer,
        "feedback": feedback,
        "timestamp": request.date.isoformat() if request.date else None
    }
    feedback_data.append(feedback_entry)
    
    # Ghi lại vào file
    if write_json(feedback_file, feedback_data):
        return jsonify({"success": True})
    return jsonify({"error": "Lỗi khi lưu phản hồi."}), 500

@app.route("/api/feedback-stats")
def get_feedback_stats():
    if "username" not in session:
        return jsonify({"error": "Chưa đăng nhập."}), 401
    feedback_data = read_json(feedback_file) or []
    
    # Tính thống kê theo file
    stats = {}
    for entry in feedback_data:
        file = entry["file"]
        feedback = entry["feedback"]
        if file not in stats:
            stats[file] = {"likes": 0, "dislikes": 0}
        if feedback == "like":
            stats[file]["likes"] += 1
        elif feedback == "dislike":
            stats[file]["dislikes"] += 1
    
    return jsonify(stats)

@app.route("/")
def serve_index():
    return send_from_directory("static", "login.html")

@app.route("/chatbot")
def serve_chatbot():
    if "username" not in session:
        return send_from_directory("static", "login.html")
    return send_from_directory("static", "index.html")

@app.route("/stats")
def serve_stats():
    if "username" not in session:
        return send_from_directory("static", "login.html")
    return send_from_directory("static", "stats.html")

if __name__ == "__main__":
    app.run(debug=True, port=5000)