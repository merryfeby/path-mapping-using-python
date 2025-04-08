import pygame
import sys
import math
import heapq

# Inisialisasi Pygame
pygame.init()

# Muat gambar peta
try:
    map_image = pygame.image.load("map2.jpg")
except pygame.error as e:
    print("Error: Tidak dapat memuat gambar peta 'map2.jpg'. Pastikan file ada di folder yang sama.")
    sys.exit(1)

map_rect = map_image.get_rect()

# Ukuran layar sesuai gambar peta, tambahkan ruang untuk tombol dan path display
screen = pygame.display.set_mode((map_rect.width, map_rect.height + 50))
pygame.display.set_caption("Rute Terbaik dengan A*")

# Koordinat rumah (manual, dalam piksel)
houses = {
    "Dental": (200, 120),  
    "Bakmi": (210, 750), 
    "Gereja": (700, 780), 
    "Nutrihub": (430, 770), 
}

# Koordinat persimpangan (manual, dalam piksel)
intersections = {
    "A": (40, 30),  
    "B": (680, 30),   
    "C": (40, 120),   
    "D": (680, 780),   
    "E": (40, 210),  
    "F": (300, 495),   
    "G": (40, 240),   
    "H": (495, 120),   
    "I": (495, 450),   
    "J": (40, 430),  
    "K": (690, 470),   
    "L": (40, 480),   
    "M": (690, 520),
    "N": (40, 770),
    "O": (495, 240),
    "P": (495, 210),
    "Q": (300, 770),
    "R": (210, 770),
}

# Graf jalan dengan path cost yang lebih kecil dan sesuai dengan peta
graph = {
    "A": {"B": 64, "C": 9},
    "B": {"A": 64, "K": 18},
    "C": {"A": 9, "H": 9, "E": 45},
    "D": {"N": 64, "M": 16, "Q": 26},
    "E": {"C": 9, "G": 3, "P": 35}, 
    "F": {"M": 19, "L": 20, "Q": 19},
    "G": {"E": 3, "J": 19, "O": 21},
    "H": {"C": 18, "P": 9},
    "I": {"J": 19, "O": 21, "K": 19},
    "J": {"I": 19, "G": 5, "L": 26},
    "K": {"B": 19, "M": 5},
    "L": {"J": 5, "N": 29, "F": 20},
    "M": {"K": 5, "D": 26, "F": 19},
    "N": {"L": 29, "D": 64, "Q": 64, "R": 64},
    "O": {"I": 21, "P": 3, "G": 21},
    "P": {"O": 3, "H": 9, "E": 45},
    "Q": {"N": 64, "F": 19, "D": 26, "R": 26},
    "R": {"Q": 26, "N": 64},
}

# Fungsi untuk menghitung jarak Euclidean antara dua titik (digunakan sebagai heuristik)
def calculate_distance(pos1, pos2):
    return math.sqrt((pos2[0] - pos1[0]) ** 2 + (pos2[1] - pos1[1]) ** 2)

# Algoritma A* untuk mencari rute terpendek
def a_star(graph, start, end, intersections):
    # Priority queue untuk menyimpan simpul yang akan dieksplorasi
    open_set = [(0, start)]  # (f_score, node)
    came_from = {node: None for node in graph}
    g_score = {node: float('infinity') for node in graph}  # Biaya aktual dari start ke node
    g_score[start] = 0
    f_score = {node: float('infinity') for node in graph}  # f_score = g_score + h_score
    f_score[start] = calculate_distance(intersections[start], intersections[end])

    while open_set:
        current_f, current = heapq.heappop(open_set)

        if current == end:
            # Rekonstruksi jalur
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
                # Heuristik: jarak Euclidean dari neighbor ke end
                h_score = calculate_distance(intersections[neighbor], intersections[end])
                f_score[neighbor] = g_score[neighbor] + h_score
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return [], 0  # Jika tidak ada jalur

# Variabel untuk menyimpan titik start, end, path, dan total cost
start_point = None
end_point = None
path = None
total_cost = 0

# Tombol Reset (koordinat dan ukuran)
reset_button_rect = pygame.Rect(10, map_rect.height + 10, 100, 30)

# Fungsi untuk menggambar tombol
def draw_button():
    pygame.draw.rect(screen, (255, 0, 0), reset_button_rect)
    font = pygame.font.Font(None, 24)
    text = font.render("Reset", True, (255, 255, 255))
    text_rect = text.get_rect(center=reset_button_rect.center)
    screen.blit(text, text_rect)

# Fungsi untuk memformat path dengan format yang diminta
def format_path(start, end, path_nodes, cost):
    path_str = f"Path: {start} → "
    for node in path_nodes:
        path_str += f"{node} → "
    path_str += f"{end} (Cost: {int(cost)})"
    return path_str

# Fungsi untuk mereset semua pilihan
def reset():
    global start_point, end_point, path, total_cost
    start_point = None
    end_point = None
    path = None
    total_cost = 0
    print("Reset titik start, end, dan rute.")

# Loop utama
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            # Cek apakah tombol reset diklik
            if reset_button_rect.collidepoint(mouse_pos):
                reset()
            else:
                # Cek apakah klik berada dekat dengan salah satu rumah
                for house_name, house_pos in houses.items():
                    if calculate_distance(mouse_pos, house_pos) < 20:  # Toleransi 20 piksel
                        if start_point is None:
                            start_point = house_name
                            print(f"Start: {start_point}")
                            path = None  # Reset path jika memilih start baru
                        elif end_point is None and house_name != start_point:
                            end_point = house_name
                            print(f"End: {end_point}")
                            # Tentukan simpul terdekat dari start_point dan end_point
                            start_node = min(intersections, key=lambda node: calculate_distance(houses[start_point], intersections[node]))
                            end_node = min(intersections, key=lambda node: calculate_distance(houses[end_point], intersections[node]))
                            # Hitung rute menggunakan A*
                            path, total_cost = a_star(graph, start_node, end_node, intersections)
                            print(f"Rute terbaik (A*): {path}")
                            print(f"Total cost: {total_cost}")
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:  # Tekan 'R' untuk reset
                reset()

    # Bersihkan layar
    screen.fill((255, 255, 255))  # Latar belakang putih

    # Gambar peta
    screen.blit(map_image, map_rect)

    # Gambar tombol reset
    draw_button()

    # Gambar titik rumah
    for house_name, house_pos in houses.items():
        pygame.draw.circle(screen, (255, 0, 0), house_pos, 5)  # Lingkaran merah untuk rumah
        # Tambahkan label nama rumah
        font = pygame.font.Font(None, 24)
        text = font.render(house_name, True, (0, 0, 0))
        screen.blit(text, (house_pos[0] + 15, house_pos[1] - 10))

    # Gambar titik persimpangan
    for intersection_name, intersection_pos in intersections.items():
        pygame.draw.circle(screen, (0, 0, 139), intersection_pos, 5)  # Lingkaran biru tua untuk persimpangan
        # Tambahkan label nama persimpangan
        font = pygame.font.Font(None, 24)
        text = font.render(intersection_name, True, (0, 0, 0))
        screen.blit(text, (intersection_pos[0] + 15, intersection_pos[1] - 10))

    # Gambar titik start dan end jika sudah dipilih
    if start_point:
        pygame.draw.circle(screen, (0, 255, 0), houses[start_point], 7, 2)  # Hijau untuk start
    if end_point:
        pygame.draw.circle(screen, (0, 0, 255), houses[end_point], 7, 2)  # Biru untuk end

    # Gambar rute jika sudah dihitung
    if path and len(path) > 1:
        for i in range(len(path) - 1):
            start_pos = intersections[path[i]]
            end_pos = intersections[path[i + 1]]
            pygame.draw.line(screen, (255, 255, 0), start_pos, end_pos, 3)  # Garis kuning untuk rute
            
        # Gambar garis dari rumah ke simpul terdekat
        if start_point:
            start_node = min(intersections, key=lambda node: calculate_distance(houses[start_point], intersections[node]))
            pygame.draw.line(screen, (255, 255, 0), houses[start_point], intersections[start_node], 3)
        if end_point:
            end_node = min(intersections, key=lambda node: calculate_distance(houses[end_point], intersections[node]))
            pygame.draw.line(screen, (255, 255, 0), houses[end_point], intersections[end_node], 3)
            
            # Format dan tampilkan jalur seperti contoh
            formatted_path = format_path(start_point if start_point else "", end_point if end_point else "", path, total_cost)
            path_font = pygame.font.Font(None, 28)
            path_text = path_font.render(formatted_path, True, (0, 0, 0))
            screen.blit(path_text, (50, map_rect.height + 15))

    pygame.display.flip()

pygame.quit()
sys.exit()