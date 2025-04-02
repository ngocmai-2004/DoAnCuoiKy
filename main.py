import heapq
import googlemaps
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from flask import Flask, request, jsonify

# Khởi tạo API Google Maps với API key
gmaps = googlemaps.Client(key='YOUR_GOOGLE_MAPS_API_KEY')

# Khởi tạo Flask để xây dựng API\app = Flask(__name__)

# Hàm thực hiện thuật toán Dijkstra để tìm đường đi ngắn nhất
def dijkstra(graph, start, end):
    queue = [(0, start)]  # Hàng đợi ưu tiên để xử lý các nút
    distances = {node: float('inf') for node in graph}  # Lưu khoảng cách từ điểm bắt đầu
    distances[start] = 0
    previous_nodes = {node: None for node in graph}  # Lưu đường đi trước của mỗi nút
    
    while queue:
        current_distance, current_node = heapq.heappop(queue)
        if current_node == end:
            break
        
        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_node
                heapq.heappush(queue, (distance, neighbor))
    
    # Truy vết lại đường đi ngắn nhất
    path, node = [], end
    while node is not None:
        path.insert(0, node)
        node = previous_nodes[node]
    
    return path, distances[end]

# Hàm gọi Google Maps API để lấy thời gian di chuyển thực tế
def get_travel_time(origin, destination):
    directions = gmaps.directions(origin, destination, mode="driving")
    return directions[0]['legs'][0]['duration']['value'] if directions else None

# Hàm huấn luyện mô hình học máy để dự đoán giao thông
def train_traffic_model(data):
    X, y = np.array(data['features']), np.array(data['labels'])
    model = RandomForestRegressor(n_estimators=100)
    model.fit(X, y)
    return model

# Hàm dự đoán tình trạng giao thông dựa vào mô hình học máy
def predict_traffic(model, features):
    return model.predict([features])[0]

# Biểu đồ đồ thị các nút và trọng số tương ứng
graph = {
    'A': {'B': 4, 'C': 2},
    'B': {'A': 4, 'D': 5},
    'C': {'A': 2, 'D': 8},
    'D': {'B': 5, 'C': 8}
}

# API lấy tuyến đường tối ưu dựa trên Dijkstra
@app.route('/route', methods=['GET'])
def get_route():
    start = request.args.get('start')
    end = request.args.get('end')
    if start not in graph or end not in graph:
        return jsonify({'error': 'Invalid locations'}), 400
    shortest_path, distance = dijkstra(graph, start, end)
    return jsonify({'shortest_path': shortest_path, 'distance': distance})

# API lấy thời gian di chuyển thực tế từ Google Maps API
@app.route('/travel_time', methods=['GET'])
def get_time():
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    travel_time = get_travel_time(origin, destination)