<<<<<<< HEAD
import heapq
import requests
from typing import Dict, List, Tuple

# Giả lập dữ liệu giao thông từ Google Maps API (thay bằng API thật trong thực tế)
def fetch_traffic_data(start: str, end: str) -> float:
    # Trong thực tế, sử dụng requests.get() để gọi Google Maps Distance Matrix API
    # Giả lập thời gian di chuyển (phút) dựa trên khoảng cách và tình trạng giao thông
    mock_data = {
        ("A", "B"): 10.0, ("A", "C"): 15.0, ("B", "D"): 20.0, 
        ("C", "D"): 10.0, ("B", "C"): 5.0
    }
    return mock_data.get((start, end), float('inf'))

# Xây dựng đồ thị từ dữ liệu giao thông
def build_graph(locations: List[str]) -> Dict[str, Dict[str, float]]:
    graph = {}
    for start in locations:
        graph[start] = {}
        for end in locations:
            if start != end:
                graph[start][end] = fetch_traffic_data(start, end)
    return graph

# Thuật toán Dijkstra để tìm đường ngắn nhất
def dijkstra(graph: Dict[str, Dict[str, float]], start: str, end: str) -> Tuple[float, List[str]]:
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    previous = {node: None for node in graph}
    pq = [(0, start)]
    
    while pq:
        current_distance, current_node = heapq.heappop(pq)
        
        if current_node == end:
            break
        
        if current_distance > distances[current_node]:
            continue
        
        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight
            
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_node
                heapq.heappush(pq, (distance, neighbor))
    
    # Xây dựng đường đi
    path = []
    current_node = end
    while current_node is not None:
        path.append(current_node)
        current_node = previous[current_node]
    path.reverse()
    
    return distances[end], path

# Mô phỏng cập nhật thời gian thực
def update_route_realtime(graph: Dict[str, Dict[str, float]], start: str, end: str) -> Tuple[float, List[str]]:
    # Giả lập cập nhật giao thông (giảm hoặc tăng thời gian ngẫu nhiên)
    for node in graph:
        for neighbor in graph[node]:
            graph[node][neighbor] *= 1.1  # Tăng 10% thời gian do tắc đường
    return dijkstra(graph, start, end)

# Hàm chính để chạy hệ thống
def main():
    # Danh sách các điểm giao hàng
    locations = ["A", "B", "C", "D"]
    
    # Xây dựng đồ thị từ dữ liệu giao thông
    graph = build_graph(locations)
    
    # Tính toán tuyến đường ban đầu
    start, end = "A", "D"
    distance, path = dijkstra(graph, start, end)
    print(f"Tuyến đường ban đầu: {path}, Thời gian: {distance} phút")
    
    # Cập nhật thời gian thực
    updated_distance, updated_path = update_route_realtime(graph, start, end)
    print(f"Tuyến đường cập nhật: {updated_path}, Thời gian: {updated_distance} phút")

if __name__ == "__main__":
    main()
=======
import os
import json
import csv
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS


app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)


data_directory = 'data/'


API_KEY = "AIzaSyDe4ZTpmEQSATWA6gawvxkQ6_ah9q3pAs8"  
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
            return "❗ Error from AI."
    else:
        return f"❌ Error: {response.status_code} - {response.text}"


def read_txt(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        return f"❗ Error when reading file {file_path}: {str(e)}"

def read_json(file_path):
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
        return f"❗ Error when reading file  {file_path}: {str(e)}"

def process_data_files(directory):
    file_data = {}
    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        if os.path.isfile(file_path):
            ext = file_name.split('.')[-1].lower()
            if ext == 'txt':
                content = read_txt(file_path)
            elif ext == 'json':
                content = read_json(file_path)
            elif ext == 'csv':
                content = read_csv(file_path)
            else:
                content = f"❗ Error when reading file  {ext}."
            file_data[file_name] = content
    return file_data


file_data = process_data_files(data_directory)

@app.route("/api/files")
def get_files():
    return jsonify(list(file_data.keys()))

@app.route("/api/file-content")
def get_file_content():
    file = request.args.get('file')
    content = file_data.get(file, "")
    if isinstance(content, str):
        return jsonify({"content": content[:1000]}) 
    else:
        return jsonify({"content": json.dumps(content, ensure_ascii=False)[:1000]})

@app.route("/api/ask", methods=["POST"])
def ask_question():
    data_input = request.get_json()
    file = data_input.get("file")
    question = data_input.get("question")
    content = file_data.get(file, "")
    if isinstance(content, dict):
        content = json.dumps(content, ensure_ascii=False)
    prompt = f"{content}\nQuestion: {question}"
    response = ask_gemini(prompt)
    return jsonify({"answer": response})


@app.route("/")
def serve_index():
    return send_from_directory("static", "index.html")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
>>>>>>> e5f1dedf (Initial commit: deploy bank_proj to DoAnCuoiKy repo)
