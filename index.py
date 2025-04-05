import pygame
import sys
import math

# Inisialisasi Pygame
pygame.init()

# Muat gambar peta
try:
    map_image = pygame.image.load("map2.jpg")
except pygame.error as e:
    print("Error: Tidak dapat memuat gambar peta 'map.png'. Pastikan file ada di folder yang sama.")
    sys.exit(1)

map_rect = map_image.get_rect()

# Ukuran layar sesuai gambar peta, tambahkan ruang untuk tombol
screen = pygame.display.set_mode((map_rect.width, map_rect.height + 50))  # Tambah 50 piksel untuk tombol
pygame.display.set_caption("Rute Terbaik")

# Koordinat rumah (manual, dalam piksel)
houses = {
    "Maximilian Dental Center": (200, 100),  
    "Bakmi Maknyus": (210, 750), 
    "SMTB": (700, 780), 
    "Nutrihub": (450, 750), 
}

# Koordinat persimpangan (manual, dalam piksel)
intersections = {
    "A": (200, 300),  # Jl. Pucang Anom & Jl. Kalibokor
    "B": (300, 400),  # Jl. Pucang Anom & Jl. Ngagel Jaya Utara
    "C": (350, 450),  # Jl. Kalibokor & Jl. Ngagel Jaya Utara
    "D": (150, 200),  # Jl. Pucang Anom Timur II & Jl. Kalibokor
}

# Graf jalan (manual, dengan jarak dalam piksel)
graph = {
    "A": {"B": 141, "C": 161, "D": 112},
    "B": {"A": 141, "C": 71},
    "C": {"A": 161, "B": 71, "D": 254},
    "D": {"A": 112, "C": 254},
}

# Fungsi untuk menghitung jarak Euclidean antara dua titik
def calculate_distance(pos1, pos2):
    return math.sqrt((pos2[0] - pos1[0]) ** 2 + (pos2[1] - pos1[1]) ** 2)

# Algoritma Dijkstra untuk mencari rute terpendek
def dijkstra(graph, start, end):
    distances = {node: float('infinity') for node in graph}
    distances[start] = 0
    previous = {node: None for node in graph}
    unvisited = list(graph.keys())

    while unvisited:
        current = min(unvisited, key=lambda node: distances[node])
        if current == end:
            break
        unvisited.remove(current)

        for neighbor, weight in graph[current].items():
            distance = distances[current] + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current

    # Rekonstruksi jalur
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = previous[current]
    path.reverse()
    return path

# Variabel untuk menyimpan titik start, end, dan path
start_point = None
end_point = None
path = None

# Tombol Reset (koordinat dan ukuran)
reset_button_rect = pygame.Rect(10, map_rect.height + 10, 100, 30)  # Tombol di kiri bawah

# Fungsi untuk menggambar tombol
def draw_button():
    pygame.draw.rect(screen, (255, 0, 0), reset_button_rect)  # Tombol merah
    font = pygame.font.Font(None, 24)
    text = font.render("Reset", True, (255, 255, 255))
    text_rect = text.get_rect(center=reset_button_rect.center)
    screen.blit(text, text_rect)

# Fungsi untuk mereset semua pilihan
def reset():
    global start_point, end_point, path
    start_point = None
    end_point = None
    path = None
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
                            # Hitung rute
                            path = dijkstra(graph, start_node, end_node)
                            print(f"Rute terbaik: {path}")
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

    pygame.display.flip()

pygame.quit()
sys.exit()