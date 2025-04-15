import os
import json
import csv
import requests

# Đường dẫn đến thư mục data
data_directory = 'data/'

# API key và URL của Gemini
API_KEY = "AIzaSyDe4ZTpmEQSATWA6gawvxkQ6_ah9q3pAs8"  # Thay bằng key của bạn
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

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
            return "❗ Không thể đọc phản hồi từ AI."
    else:
        return f"❌ Lỗi: {response.status_code} - {response.text}"

# Đọc dữ liệu từ các file .txt
def read_txt(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        return f"❗ Lỗi khi đọc file {file_path}: {str(e)}"

# Đọc dữ liệu từ các file .json
def read_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        return f"❗ Lỗi khi đọc file {file_path}: {str(e)}"

# Đọc dữ liệu từ các file .csv
def read_csv(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            data = "\n".join([", ".join(row) for row in reader])
            return data
    except Exception as e:
        return f"❗ Lỗi khi đọc file {file_path}: {str(e)}"

# Hàm xử lý các file trong thư mục data
def process_data_files(directory):
    file_data = {}

    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        
        # Kiểm tra nếu là file
        if os.path.isfile(file_path):
            file_extension = file_name.split('.')[-1].lower()
            
            if file_extension == 'txt':
                content = read_txt(file_path)
            elif file_extension == 'json':
                content = read_json(file_path)
            elif file_extension == 'csv':
                content = read_csv(file_path)
            else:
                content = f"❗ Không hỗ trợ loại file {file_extension}."
            
            # Lưu nội dung của file vào dictionary
            file_data[file_name] = content
    
    return file_data

# Hàm hỏi và đáp dựa trên nội dung của file
def chat_with_files(file_data):
    print("\n🤖 Gemini AI Chatbot (gõ 'exit' để thoát)")
    
    while True:
        # Hiển thị các file có trong thư mục
        print("\nCác file trong thư mục data:")
        for file_name in file_data:
            print(f"- {file_name}")
        
        # Yêu cầu người dùng chọn file để hỏi
        selected_file = input("\nChọn file để hỏi (hoặc gõ 'exit' để thoát): ")
        
        if selected_file.lower() == 'exit':
            print("Tạm biệt! 👋")
            break
        
        # Kiểm tra nếu file có trong dữ liệu
        if selected_file in file_data:
            print(f"\nĐang sử dụng file: {selected_file}")
            content = file_data[selected_file]
            print(f"Nội dung file:\n{content[:500]}...")  # In ra 500 ký tự đầu tiên của file
            
            # Yêu cầu người dùng nhập câu hỏi
            question = input("\nBạn: ")
            if question.lower() in ['exit', 'quit']:
                print("Tạm biệt! 👋")
                break
            
            # Gửi câu hỏi và nhận phản hồi từ Gemini
            response = ask_gemini(f"{content}\nCâu hỏi: {question}")
            print(f"AI: {response}\n")
        else:
            print(f"❗ Không tìm thấy file '{selected_file}'. Vui lòng chọn lại.")

# Chạy xử lý các file trong thư mục 'data' và thực hiện hỏi đáp
file_data = process_data_files(data_directory)
chat_with_files(file_data)
