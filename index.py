import pygame
import sys
import math
import heapq

pygame.init()

try:
    map_image = pygame.image.load("map2.jpg")
except pygame.error as e:
    print("Error")
    sys.exit(1)

map_rect = map_image.get_rect()

screen = pygame.display.set_mode((map_rect.width, map_rect.height + 50))

houses = {
    "Dental": (200, 100),  
    "Bakmi": (210, 750), 
    "Gereja": (700, 790), 
    "Nutrihub": (430, 760), 
}

intersections = {
    "A": (40, 30),  
    "B": (690, 30),   
    "C": (40, 120),   
    "D": (680, 790),   
    "E": (40, 215),  
    "F": (300, 495),   
    "G": (40, 240),   
    "H": (495, 120),   
    "I": (495, 460),   
    "J": (40, 425),  
    "K": (690, 475),   
    "L": (40, 480),   
    "M": (690, 525),
    "N": (40, 770),
    "O": (495, 240),
    "P": (495, 210),
    "Q": (300, 770),
    "R": (210, 770),
    "S": (200, 120),  
    "V": (430, 780),  
}

graph = {
    "A": {"B": 60, "C": 10},
    "B": {"A": 60, "K": 45},
    "C": {"A": 10, "H": 46, "E": 10, "S": 16},  
    "D": {"N": 60, "M": 14, "Q": 38, "V": 25}, 
    "E": {"C": 10, "G": 3, "P": 35}, 
    "F": {"M": 39, "L": 26, "Q": 28},
    "G": {"E": 3, "J": 20, "O": 21},
    "H": {"C": 46, "P": 3, "S": 30},           
    "I": {"J": 35, "O": 22, "K": 2},
    "J": {"I": 35, "G": 20, "L": 6},
    "K": {"B": 45, "M": 5, "I": 2},
    "L": {"J": 6, "N": 29, "F": 26},
    "M": {"K": 5, "D": 14, "F": 39},
    "N": {"L": 29, "D": 60, "Q": 13, "R": 1},
    "O": {"I": 22, "P": 3, "G": 21},
    "P": {"O": 3, "H": 3, "E": 35},
    "Q": {"N": 13, "F": 28, "D": 38, "R": 9, "V": 13},  
    "R": {"Q": 9, "N": 1},                     
    "S": {"C": 16, "H": 30},                    
    "V": {"Q": 13, "D": 25},                   
}

house_to_intersection = {
    "Dental": "S",    
    "Bakmi": "R",     
    "Gereja": "D",   
    "Nutrihub": "V", 
}

def calculate_distance(pos1, pos2):
    return math.sqrt((pos2[0] - pos1[0]) ** 2 + (pos2[1] - pos1[1]) ** 2)

def a_star(graph, start, end, intersections):
    open_set = [(0, start)]  # (f_score, node)
    came_from = {node: None for node in graph}
    g_score = {node: float('infinity') for node in graph}
    g_score[start] = 0
    f_score = {node: float('infinity') for node in graph}
    f_score[start] = calculate_distance(intersections[start], intersections[end])

    while open_set:
        current_f, current = heapq.heappop(open_set)

        if current == end:
            path = []
            while current is not None:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path, g_score[end]

        for neighbor, weight in graph[current].items():
            tentative_g_score = g_score[current] + weight

            if tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                h_score = calculate_distance(intersections[neighbor], intersections[end])
                f_score[neighbor] = g_score[neighbor] + h_score
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return [], 0  # Jika tidak ada jalur

# Variabel untuk menyimpan titik-titik yang akan dikunjungi dan rute-rutenya
selected_points = []  # Daftar titik (nama dan tipe) yang dipilih
routes = []  # Daftar rute antar titik berurutan
total_route_cost = 0

reset_button_rect = pygame.Rect(10, map_rect.height + 10, 100, 30)
status_message = ""

def draw_interface():
    # Tombol Reset
    pygame.draw.rect(screen, (255, 0, 0), reset_button_rect)
    font = pygame.font.Font(None, 24)
    text = font.render("Reset", True, (255, 255, 255))
    text_rect = text.get_rect(center=reset_button_rect.center)
    screen.blit(text, text_rect)

def reset():
    global selected_points, routes, total_route_cost, status_message
    selected_points = []
    routes = []
    total_route_cost = 0
    status_message = "Reset semua titik dan rute."
    print("Reset semua titik dan rute.")

def calculate_routes():
    global routes, total_route_cost, status_message
    
    if len(selected_points) < 2:
        status_message = "Minimal harus memilih 2 titik untuk menghitung rute!"
        print(status_message)
        return
    
    routes = []
    total_route_cost = 0
    
    # Hitung rute antara titik-titik berurutan
    for i in range(len(selected_points) - 1):
        start_point, start_type = selected_points[i]
        end_point, end_type = selected_points[i + 1]
        
        # Tentukan node untuk start dan end
        start_node = house_to_intersection[start_point] if start_type == "house" else start_point
        end_node = house_to_intersection[end_point] if end_type == "house" else end_point
        
        # Hitung rute menggunakan A*
        path, path_cost = a_star(graph, start_node, end_node, intersections)
        
        if path:  # Jika ada jalur
            segment_cost = path_cost
            # Tambahkan cost Euclidean jika start/end adalah rumah
            if start_type == "house":
                start_to_node_cost = calculate_distance(houses[start_point], intersections[start_node]) / 10
                segment_cost += start_to_node_cost
            if end_type == "house":
                node_to_end_cost = calculate_distance(intersections[end_node], houses[end_point]) / 10
                segment_cost += node_to_end_cost
                
            # Simpan rute untuk segmen ini
            routes.append({
                'start_point': start_point,
                'start_type': start_type,
                'end_point': end_point,
                'end_type': end_type,
                'start_node': start_node,
                'end_node': end_node,
                'path': path,
                'cost': segment_cost
            })
            
            total_route_cost += segment_cost
            print(f"Rute {i+1}: {start_point} ke {end_point}, Cost: {segment_cost:.2f}")
        else:
            print(f"Tidak ada rute yang ditemukan antara {start_point} dan {end_point}!")
            status_message = f"Tidak ada rute antara {start_point} dan {end_point}!"
            return
    
    status_message = ""
    print(f"Total cost untuk semua rute: {total_route_cost:.2f}")

# Loop utama
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            # Cek tombol reset
            if reset_button_rect.collidepoint(mouse_pos):
                reset()
            else:
                # Cek klik pada rumah atau persimpangan
                selected_point = None
                selected_type = None

                # Cek rumah
                for house_name, house_pos in houses.items():
                    if calculate_distance(mouse_pos, house_pos) < 20:
                        selected_point = house_name
                        selected_type = "house"
                        break
                # Cek persimpangan jika belum memilih rumah
                if not selected_point:
                    for intersection_name, intersection_pos in intersections.items():
                        if calculate_distance(mouse_pos, intersection_pos) < 20:
                            selected_point = intersection_name
                            selected_type = "intersection"
                            break

                if selected_point:
                    # Hapus titik jika sudah terpilih sebelumnya
                    already_selected = False
                    for i, (point, point_type) in enumerate(selected_points):
                        if point == selected_point and point_type == selected_type:
                            selected_points.pop(i)
                            status_message = f"Menghapus titik: {selected_point}"
                            print(f"Menghapus titik: {selected_point}")
                            already_selected = True
                            # Hitung ulang rute karena titik berubah
                            if len(selected_points) >= 2:
                                calculate_routes()
                            else:
                                routes = []
                                total_route_cost = 0
                            break
                    
                    # Tambahkan titik baru jika belum terpilih
                    if not already_selected:
                        selected_points.append((selected_point, selected_type))
                        status_message = f"Titik {len(selected_points)}: {selected_point}"
                        print(f"Titik {len(selected_points)}: {selected_point} ({selected_type})")
                        # Hitung ulang rute jika sudah ada minimal 2 titik
                        if len(selected_points) >= 2:
                            calculate_routes()
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reset()

    # Clear screen
    screen.fill((255, 255, 255))

    # Gambar peta
    screen.blit(map_image, map_rect)

    # Gambar UI 
    draw_interface()

    # Gambar titik rumah
    for house_name, house_pos in houses.items():
        pygame.draw.circle(screen, (255, 0, 0), house_pos, 5)
        font = pygame.font.Font(None, 24)
        text = font.render(house_name, True, (0, 0, 0))
        screen.blit(text, (house_pos[0] + 15, house_pos[1] - 10))

    # Gambar titik persimpangan
    for intersection_name, intersection_pos in intersections.items():
        pygame.draw.circle(screen, (0, 0, 139), intersection_pos, 5)
        font = pygame.font.Font(None, 24)
        text = font.render(intersection_name, True, (0, 0, 0))
        screen.blit(text, (intersection_pos[0] + 15, intersection_pos[1] - 10))

    # Gambar titik-titik yang terpilih dengan nomor urutan
    for i, (point, point_type) in enumerate(selected_points):
        pos = houses[point] if point_type == "house" else intersections[point]
        pygame.draw.circle(screen, (0, 255, 0), pos, 10, 2)
        
        # Tambahkan nomor urutan
        font = pygame.font.Font(None, 28)
        number_text = font.render(str(i + 1), True, (0, 0, 0))
        number_rect = number_text.get_rect(center=pos)
        screen.blit(number_text, number_rect)

    # Gambar rute-rute jika sudah dihitung
    for route in routes:
        path = route['path']
        if len(path) > 1:
            # Gambar rute antara persimpangan/node
            for i in range(len(path) - 1):
                start_pos = intersections[path[i]]
                end_pos = intersections[path[i + 1]]
                pygame.draw.line(screen, (255, 255, 0), start_pos, end_pos, 3)
            
            # Gambar garis dari rumah ke simpul terdekat jika start/end adalah rumah
            if route['start_type'] == "house":
                pygame.draw.line(screen, (255, 255, 0), houses[route['start_point']], 
                                intersections[route['start_node']], 3)
            if route['end_type'] == "house":
                pygame.draw.line(screen, (255, 255, 0), houses[route['end_point']], 
                                intersections[route['end_node']], 3)
    
    # Tampilkan total cost jika rute sudah dihitung - HANYA SATU KALI
    if routes and total_route_cost > 0:
        font = pygame.font.Font(None, 28)
        cost_text = font.render(f"Total Cost: {total_route_cost:.2f}", True, (0, 0, 0))
        screen.blit(cost_text, (130, map_rect.height + 15))

    # Tampilkan status message, hanya jika ada status message
    if status_message:
        font = pygame.font.Font(None, 24)
        text = font.render(status_message, True, (0, 0, 0))
        screen.blit(text, (300, map_rect.height + 15))

    pygame.display.flip()

pygame.quit()
sys.exit()