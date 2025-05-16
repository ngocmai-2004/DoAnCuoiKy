
import os
import json
import csv
import requests
from datetime import datetime

# Đường dẫn đến thư mục data và các file log
data_directory = 'data/'
unrecognized_log_file = 'unrecognized_questions.txt'
response_log_file = 'response_log.txt'

# API key và URL
API_KEY = "AIzaSyDe4ZTpmEQSATWA6gawvxkQ6_ah9q3pAs8"  
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"


def log_unrecognized_question(question):
    try:
        with open(unrecognized_log_file, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] Câu hỏi: {question}\n")
    except Exception as e:
        print(f"❗ Lỗi khi ghi nhận câu hỏi: {str(e)}")


def log_response(question, response):
    try:
        with open(response_log_file, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] Câu hỏi: {question}\n")
            f.write(f"[{timestamp}] Trả lời: {response}\n\n")
    except Exception as e:
        print(f"❗ Lỗi khi ghi nhận câu trả lời: {str(e)}")

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

    try:
        response = requests.post(API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            data = response.json()
            try:
                ai_response = data['candidates'][0]['content']['parts'][0]['text']
                # Kiểm tra nếu phản hồi không hữu ích
                if len(ai_response.strip()) < 10 or "lỗi" in ai_response.lower():
                    return None
                return ai_response
            except (KeyError, IndexError):
                return None
        else:
            return None
    except Exception as e:
        print(f"❗ Lỗi khi gọi API: {str(e)}")
        return None

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
            
            file_data[file_name] = content
    
    return file_data

# Hàm hỏi và đáp dựa trên nội dung của file
def chat_with_files(file_data):
    print("\n🤖 Gemini AI Chatbot (gõ 'exit' để thoát)")
    
    while True:
        print("\nCác file trong thư mục data:")
        for file_name in file_data:
            print(f"- {file_name}")
        
        selected_file = input("\nChọn file để hỏi (hoặc gõ 'exit' để thoát): ")
        
        if selected_file.lower() == 'exit':
            print("Tạm biệt! 👋")
            break
        
        if selected_file in file_data:
            print(f"\nĐang sử dụng file: {selected_file}")
            content = file_data[selected_file]
            print(f"Nội dung file:\n{content[:500]}...")
            
            question = input("\nBạn: ")
            if question.lower() in ['exit', 'quit']:
                print("Tạm biệt! 👋")
                break
            
            response = ask_gemini(f"{content}\nCâu hỏi: {question}")
            if response:
                print(f"AI: {response}\n")
                log_response(question, response)
            else:
                default_response = "Hiện tại chatbot AI chưa được train kiến thức này, sẽ ghi nhận và phát triển thêm trong tương lai."
                print(f"AI: {default_response}\n")
                log_unrecognized_question(question)
                log_response(question, default_response)
        else:
            print(f"❗ Không tìm thấy file '{selected_file}'. Vui lòng chọn lại.")


file_data = process_data_files(data_directory)
chat_with_files(file_data)