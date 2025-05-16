import json
import os
from tkinter import messagebox

# Đường dẫn đến file user.json
user_file = 'd:\\bank_proj\\user.json'

# Hàm đọc file JSON
def read_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"❗ Lỗi khi đọc file {file_path}: {str(e)}")
        return None

# Hàm xác thực người dùng
def authenticate_user(username, password):
    users = read_json(user_file)
    if not users:
        return None

    for user in users:
        if user['username'] == username and user['password'] == password:
            return user  # Trả về thông tin người dùng nếu xác thực thành công
    return None  # Trả về None nếu không tìm thấy

# Hàm kiểm tra quyền truy cập file
def has_permission(user, file_name):
    if file_name in user['permissions']:
        return True
    return False