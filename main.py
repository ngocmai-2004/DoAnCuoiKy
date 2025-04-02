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
