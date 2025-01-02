"""
2024-10-10: edited hybrid dithering: removed local contrast, dynamic gamma...
adjusted for better image on blured images (less detail)


"""
import numpy as np
import serial
import threading
import queue
import time
from PIL import ImageGrab, Image, ImageEnhance, ImageOps
from skimage import filters
import cv2
from datetime import datetime

# UART nustatymai
uart_port = 'COM8'  # Pakeiskite į savo UART prievadą
baud_rate = 1280000  # Baud norma
ser = serial.Serial(uart_port, baud_rate, timeout=0.003)  # Timeout, kad nelauktų amžinai

# Queue for processed images to send
image_queue = queue.Queue(maxsize=10)

previous_image = None  # Ankstesnis vaizdas

def capture_screen():
    # Fiksuoti ekraną
    screen = ImageGrab.grab()
    return screen

def resize_image(image):
    # Sumažinti vaizdą iki 128x64
    resized_image = image.resize((128, 64))
    return resized_image

def enhance_contrast(image, contrast_factor=5.0, blend_strength=1.0):
    # Padidinti kontrastą
    enhancer = ImageEnhance.Contrast(image)
    enhanced_image = enhancer.enhance(contrast_factor)  # Didinti kontrastą pagal koeficientą

    # Sujungti kontrastingą vaizdą su originaliu (blend)
    final_image = Image.blend(image.convert('L'), enhanced_image, alpha=blend_strength)
    
    return final_image

def edge_detection(image, edge_strength=1.0):
    # Konvertuoti vaizdą į pilką spektrą ir aptikti kraštus
    image_array = np.array(image.convert('L'))
    edges = filters.sobel(image_array)  # Sobel filtravimas
    
    # Normalizuoti kraštų reikšmes ir sukurti 8-bitų vaizdą
    edges = (edges * 255).astype(np.uint8)
    
    # Kraštų aptikimo vaizdą sujungti su originaliu
    edges_image = Image.fromarray(edges)
    
    # Sujungti originalų vaizdą su kraštų aptikimo vaizdu (blending)
    detailed_image = Image.blend(image.convert('L'), edges_image, alpha=edge_strength)
    
    return detailed_image

def adaptive_threshold(image, threshold_strength=0.5):
    # Konvertuoti vaizdą į pilkąjį spektrą
    image_array = np.array(image.convert('L'))  
    
    # Taikyti adaptyvų slenkstį naudojant OpenCV
    thresh = cv2.adaptiveThreshold(image_array, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 3, 1)
    
    # Konvertuoti slenkstį atgal į vaizdą
    threshold_image = Image.fromarray(thresh)
    
    # Sujungti adaptyvaus slenksčio rezultatą su originaliu paveikslu (blending)
    final_image = Image.blend(image.convert('L'), threshold_image, alpha=threshold_strength)
    
    return final_image

def apply_filters(image, threshold_filter=0.5):
    # 1. Sukurti originalaus paveikslėlio kopiją
    original_image = image.copy().convert("L")  # Konvertavimas į 2 spalvas (L - grayscale)
    
    # 2. Pritaikyti filtrus originalios kopijos versijai
    filtered_image = adaptive_threshold(image, threshold_strength=0.3)  # Adaptyvus slenkstis
    filtered_image = enhance_contrast(filtered_image, contrast_factor=1.2)  # Kontrasto didinimas
    filtered_image = edge_detection(filtered_image, edge_strength=0.5)  # Kontūrų aptikimas
    filtered_image = enhance_contrast(filtered_image, contrast_factor=3.5)  # Papildomas kontrasto didinimas

    # Užtikrinti, kad abu paveikslėliai būtų to paties dydžio
    filtered_image = filtered_image.resize(original_image.size)
    
    # 3. Konvertuoti paveikslėlius į NumPy masyvus
    original_np = np.array(original_image)
    filtered_np = np.array(filtered_image)
    
    # 4. Sujungti originalą su filtruotu paveikslėliu naudojant alpha blending
    combined_np = (threshold_filter * original_np + (1 - threshold_filter) * filtered_np).astype(np.uint8)
    
    # 5. Konvertuoti atgal į paveikslėlį
    combined_image = Image.fromarray(combined_np)

    return combined_image

def apply_gamma_correction(image_array, gamma):
    # Taikyti gamma korekciją, kad šviesios spalvos taptų dar tamsesnės
    normalized = image_array / 255.0  # Normalizuoti tarp 0 ir 1
    corrected = np.power(normalized, gamma)  # Taikyti gamma korekciją
    return (corrected * 255).astype(np.uint8)  # Normalizuoti atgal į 0-255

# Pagrindinės slenkstinės matricos
threshold_maps = {
    2: np.array([[0, 128], [192, 64]]),  # 2x2 matrica

    3: np.array([[0, 128, 32],
                 [192, 64, 224],
                 [48, 160, 96]]),  # 3x3 matrica

    4: np.array([[0, 32, 8, 40],
                 [48, 16, 56, 24],
                 [12, 44, 4, 36],
                 [60, 28, 52, 20]]),  # 4x4 matrica

    5: np.array([[0, 128, 32, 160, 8],
                 [192, 64, 224, 96, 48],
                 [40, 144, 16, 176, 56],
                 [240, 112, 208, 80, 200],
                 [24, 152, 72, 184, 104]]),  # 5x5 matrica

    6: np.array([[0, 32, 8, 40, 12, 44],
                 [48, 16, 56, 24, 52, 20],
                 [12, 44, 4, 36, 8, 28],
                 [60, 28, 48, 16, 36, 8],
                 [20, 52, 32, 4, 44, 12],
                 [32, 8, 40, 12, 48, 24]]),  # 6x6 matrica

    7: np.array([[0, 32, 8, 40, 16, 48, 24],
                 [64, 16, 96, 48, 32, 112, 56],
                 [12, 72, 4, 36, 8, 64, 40],
                 [80, 28, 112, 72, 52, 84, 60],
                 [20, 88, 40, 4, 36, 60, 16],
                 [92, 64, 24, 16, 48, 12, 72],
                 [24, 52, 32, 12, 64, 28, 36]]),  # 7x7 matrica

    8: np.array([[0, 32, 8, 40, 12, 44, 16, 48],
                 [48, 16, 56, 24, 52, 20, 60, 28],
                 [12, 44, 4, 36, 8, 32, 16, 40],
                 [60, 28, 48, 16, 36, 8, 56, 24],
                 [20, 52, 32, 4, 44, 12, 40, 12],
                 [32, 8, 40, 12, 48, 16, 60, 28],
                 [48, 16, 56, 24, 36, 8, 60, 28],
                 [12, 44, 4, 36, 48, 16, 40, 12]]),  # 8x8 matrica
    9: np.array([
        [0, 48, 12, 60, 3, 51, 15, 63, 6],
        [32, 16, 44, 28, 35, 19, 47, 31, 39],
        [8, 56, 4, 52, 11, 59, 7, 55, 14],
        [64, 24, 40, 20, 67, 27, 43, 23, 71],
        [2, 50, 10, 58, 5, 53, 9, 57, 13],
        [36, 20, 68, 32, 38, 22, 70, 36, 42],
        [16, 64, 8, 56, 12, 60, 4, 52, 20],
        [48, 24, 32, 16, 50, 26, 34, 18, 54],
        [4, 52, 12, 60, 8, 56, 4, 52, 12]
    ]),

    10: np.array([
        [0, 51, 14, 61, 5, 54, 18, 65, 9, 58],
        [34, 18, 44, 28, 37, 21, 47, 31, 41, 25],
        [10, 56, 8, 52, 12, 59, 4, 55, 11, 50],
        [64, 24, 40, 20, 67, 27, 43, 23, 71, 29],
        [2, 50, 9, 53, 5, 53, 12, 54, 6, 48],
        [36, 21, 69, 33, 38, 22, 71, 36, 44, 22],
        [18, 63, 12, 56, 14, 61, 6, 54, 21, 57],
        [54, 28, 34, 18, 53, 26, 38, 20, 55, 29],
        [6, 53, 12, 58, 9, 55, 7, 53, 12, 50],
        [20, 70, 15, 68, 25, 63, 17, 60, 28, 61]
    ]),

    11: np.array([
        [0, 48, 12, 60, 6, 51, 14, 63, 8, 57, 2],
        [33, 16, 44, 28, 35, 19, 47, 31, 38, 22, 41],
        [8, 56, 4, 52, 9, 59, 5, 55, 11, 61, 7],
        [64, 24, 40, 20, 67, 27, 43, 23, 71, 29, 67],
        [2, 50, 9, 53, 5, 53, 12, 54, 7, 49, 11],
        [36, 21, 69, 32, 38, 22, 71, 36, 45, 22, 49],
        [16, 64, 12, 56, 17, 60, 6, 54, 22, 58, 19],
        [48, 24, 32, 16, 52, 26, 35, 19, 54, 29, 53],
        [12, 52, 14, 58, 12, 56, 14, 50, 11, 52, 15],
        [54, 20, 44, 20, 48, 19, 43, 22, 50, 23, 47],
        [4, 49, 5, 50, 12, 48, 4, 53, 9, 51, 8]
    ]),

    12: np.array([
        [0, 32, 8, 40, 4, 36, 12, 44, 2, 34, 10, 42],
        [48, 16, 56, 24, 52, 20, 60, 28, 50, 18, 58, 26],
        [12, 44, 4, 36, 8, 40, 6, 38, 14, 46, 6, 38],
        [60, 28, 48, 16, 64, 32, 52, 20, 66, 30, 50, 22],
        [16, 40, 12, 36, 20, 44, 6, 38, 22, 46, 18, 42],
        [34, 22, 70, 38, 44, 24, 66, 36, 48, 30, 40, 28],
        [8, 58, 6, 52, 12, 44, 10, 36, 14, 56, 8, 40],
        [56, 32, 38, 18, 56, 34, 48, 28, 58, 30, 44, 22],
        [6, 38, 12, 46, 10, 40, 16, 50, 14, 48, 8, 42],
        [48, 16, 54, 24, 52, 18, 58, 28, 50, 22, 40, 32],
        [20, 44, 12, 36, 24, 40, 18, 42, 20, 46, 16, 48],
        [34, 26, 44, 20, 46, 22, 36, 30, 40, 18, 52, 30]
    ]),
}

def hybrid_dither(image, gamma=1.0, matrix_size=2):
    image_array = np.array(image.convert('L'))

    # Taikome gamos korekciją
    image_array = apply_gamma_correction(image_array, gamma)

    # Normalizuojame vaizdą tarp 0 ir 1
    normalized_image = image_array / 255.0

    # Gauname paveikslėlio matmenis
    height, width = image_array.shape

    # Sukuriame tuščią dither rezultatą
    dithered_image = np.zeros_like(image_array)

    # Skaičiuojame bendrą kontrastą visam paveikslėliui
    min_intensity = np.min(normalized_image)
    max_intensity = np.max(normalized_image)
    overall_contrast = max_intensity - min_intensity

    # Gauname atitinkamą slenkstinę matricą pagal matrix_size
    threshold_map = threshold_maps.get(matrix_size, threshold_maps[2])
    map_size = threshold_map.shape[0]

    # Pereiname per visą paveikslėlį pikseliais
    for y in range(height):
        for x in range(width):
            pixel_value = image_array[y, x]
            threshold = threshold_map[y % map_size, x % map_size]  # Naudoti modulių operaciją
            dithered_pixel = 255 if pixel_value > threshold else 0
            dithered_image[y, x] = dithered_pixel

    return Image.fromarray(dithered_image)

def image_to_1024_bytes(image, direction='bottom_left'):
    # Konvertuoti 128x64 monochrominį paveikslėlį į 1024 baitus (8x128 matrica)
    image_array = np.array(image)
    byte_array = []

    if direction == 'bottom_left':
        for x in range(0, 128):
            for y in range(56, -1, -8):
                byte = 0
                for bit in range(8):
                    byte |= (image_array[y + bit, x] & 1) << bit
                byte_array.append(byte)

    return byte_array

def send_data(ser):
    while True:
        byte_array = image_queue.get()  # Laukti, kol bus gautas vaizdas
        if byte_array is None:  # Tikrinti baigimo signalą
            break

        # Siųsti visą 1025 baitų masyvą vienu metu
        ser.write(bytearray(byte_array))

        # Gauti dabartinį laiką
        timestamp = datetime.now().strftime('%M:%S:%f')[:-3]  # Formatuoti MM:SS:FFF (milisekundės)

        # Spausdinti laiko žymę, kai siunčiami duomenys
        print(f'Duomenys nusiųsti: {timestamp}')

        # Laukti atsakymo iš UART
        while True:
            response = ser.readline().decode().strip()

            # Patikrinti atsakymą
            if response == "OK":
                break  # Išeiti iš laukimo ciklo, jei atsakymas OK


def start_processing():
    global previous_image  # Naudoti globalų kintamąjį
    try:
        while True:
            # Fiksuoti ekraną
            screen_image = capture_screen()

            # Konvertuoti ekraną į numpy masyvą
            current_image_data = np.array(screen_image)

            # Palyginti su ankstesniu vaizdu
            #if previous_image is not None and np.array_equal(current_image_data, previous_image):
            #    print("Vaizdai identiški, nesiunčiama.")
            #    continue  # Jei identiški, praleisti

            # Atnaujinti ankstesnį vaizdą
            previous_image = current_image_data
            # Aptinkamas išplaukęs vaizdas
            
            # Sumažinti vaizdą
            small_image = resize_image(screen_image)

            # Pritaikyti filtrus (kraštinių išryškinimas)
            filtered_image = apply_filters(small_image, threshold_filter=0.3)
            
            # Konvertuoti į monochrominį su ditherinimu (kraštinių išryškinimas)
            monochrome_image = hybrid_dither(filtered_image, gamma= 1.5, matrix_size=12)
            # Konvertuoti į 1024 baitų formatą (8 vertikalūs pikseliai į vieną baitą)
            byte_array = image_to_1024_bytes(monochrome_image)

            # Put the byte_array into the queue
            image_queue.put(byte_array)

    except KeyboardInterrupt:
        print("Apdorojimas sustabdytas.")
    finally:
        image_queue.put(None)  # Signal to sender to exit
        print("Apdorojimo srautas baigtas.")

def check_for_start():
    while True:
        start_command = ser.readline().decode().strip()  # Skaityti komandas iš UART
        if start_command == "START":
            print("Gauta START komanda, pradedamas siuntimas.")
            time.sleep(0.1)  # Palaukti prieš pradedant

            # Paleidžiame dvi gijas: apdorojimą ir siuntimą
            processing_thread = threading.Thread(target=start_processing)
            sending_thread = threading.Thread(target=send_data, args=(ser,))

            # Start threads
            processing_thread.start()
            sending_thread.start()

            # Join threads
            processing_thread.join()
            sending_thread.join()
            break

# Paleisti, kol gaunama "START" komanda
check_for_start()

# Uždaryti UART
ser.close()
