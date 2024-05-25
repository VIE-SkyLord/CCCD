import cv2
import numpy as np
import pytesseract
import re
import threading
import time
from collections import deque, Counter
from PIL import ImageFont, ImageDraw, Image
import tkinter as tk

class VideoCapture:
    def __init__(self, src=0):
        self.cap = cv2.VideoCapture(src)
        self.ret, self.frame = self.cap.read()
        self.is_running = True
        threading.Thread(target=self.update, args=()).start()

    def update(self):
        while self.is_running:
            self.ret, self.frame = self.cap.read()

    def read(self):
        return self.ret, self.frame

    def stop(self):
        self.is_running = False
        self.cap.release()
    
    def reset(self):
        return "Tỉnh thành: \nThế kỷ: \nNăm sinh: \nID ngẫu nhiên: "

    def parse_cmnd(self, cmnd):
        if len(cmnd) != 12:
            return "Số CMND không hợp lệ. Vui lòng nhập lại."

        province_code = cmnd[:3]
        century = cmnd[3]
        year_of_birth = cmnd[4:6]
        random_id = cmnd[6:]

        province_codes = {
            "001": "Hà Nội",
            "002": "Hà Giang",
            "004": "Cao Bằng",
            "006": "Bắc Kạn",
            "008": "Tuyên Quang",
            "010": "Lào Cai",
            "011": "Điện Biên",
            "012": "Lai Châu",
            "014": "Sơn La",
            "015": "Yên Bái",
            "017": "Hòa Bình",
            "019": "Thái Nguyên",
            "020": "Lạng Sơn",
            "022": "Quảng Ninh",
            "024": "Bắc Giang",
            "025": "Phú Thọ",
            "026": "Vĩnh Phúc",
            "027": "Bắc Ninh",
            "030": "Hải Dương",
            "031": "Hải Phòng",
            "033": "Hưng Yên",
            "034": "Thái Bình",
            "035": "Hà Nam",
            "036": "Nam Định",
            "037": "Ninh Bình",
            "038": "Thanh Hóa",
            "040": "Nghệ An",
            "042": "Hà Tĩnh",
            "044": "Quảng Bình",
            "045": "Quảng Trị",
            "046": "Thừa Thiên Huế",
            "048": "Đà Nẵng",
            "049": "Quảng Nam",
            "051": "Quảng Ngãi",
            "052": "Bình Định",
            "054": "Phú Yên",
            "056": "Khánh Hòa",
            "058": "Ninh Thuận",
            "060": "Bình Thuận",
            "062": "Kon Tum",
            "064": "Gia Lai",
            "066": "Đắk Lắk",
            "067": "Đắk Nông",
            "068": "Lâm Đồng",
            "070": "Bình Phước",
            "072": "Tây Ninh",
            "074": "Bình Dương",
            "075": "Đồng Nai",
            "077": "Bà Rịa - Vũng Tàu",
            "079": "Hồ Chí Minh",
            "080": "Long An",
            "082": "Tiền Giang",
            "083": "Bến Tre",
            "084": "Trà Vinh",
            "086": "Vĩnh Long",
            "087": "Đồng Tháp",
            "089": "An Giang",
            "091": "Kiên Giang",
            "092": "Cần Thơ",
            "093": "Hậu Giang",
            "094": "Sóc Trăng",
            "095": "Bạc Liêu",
            "096": "Cà Mau"
        }

        gender_codes = {
            "0": "Nam",
            "1": "Nữ",
            "2": "Nam",
            "3": "Nữ"
        }

        century_codes = {
            "0": "XX",
            "1": "XX",
            "2": "XXI",
            "3": "XXI"
        }

        def year_of_birth_codes(century):
            if century == "XX":
                return "19"
            else:
                return "20"

        province_name = province_codes.get(province_code, "Không xác định")
        century_prefix = century_codes.get(century, "Không xác định")
        gender_prefix = gender_codes.get(century, "Không xác định")
        year_of_birth_full = year_of_birth_codes(century_prefix) + year_of_birth

        return f"Tỉnh thành: {province_name}\nThế kỷ: {century_prefix}\nGiới tính: {gender_prefix}\nNăm sinh: {year_of_birth_full}\nID ngẫu nhiên: {random_id}"

def adjust_gamma(image, gamma=1.0):
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(image, table)

def draw_infoCCCD(output_text):
    output_image = np.zeros((500, 500, 3), np.uint8)
    output_image_pil = Image.fromarray(cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(output_image_pil)
    font = ImageFont.truetype("arial.ttf", 34)

    y = 250
    for line in output_text.split('\n'):
        draw.text((10, y), line, font=font, fill=(255, 255, 255, 0))
        y += 40

    output_image = cv2.cvtColor(np.array(output_image_pil), cv2.COLOR_RGB2BGR)
    cv2.imshow("Output", output_image)

def draw_cccd_number(image, cccd_number):
    fontpath = "arial.ttf"
    image_font = ImageFont.truetype(fontpath, 34)
    
    org = (10, 40)
    color = (255, 255, 255)

    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(image_pil)
    
    draw.text(org, cccd_number, font=image_font, fill=color)
    
    image = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
    
    return image

def preProcesingImage(image):
    # Chuyển ảnh sang ảnh xám
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Làm mờ ảnh để giảm nhiễu
    blur_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
    # Áp dụng phân ngưỡng cục bộ
    resultImage = cv2.adaptiveThreshold(blur_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    return resultImage

pytesseract.pytesseract.tesseract_cmd = r'D:\\Program Files\\Tesseract-OCR\\tesseract.exe'
queue_frame_length = 5

def update_queue_frame_length():
    global queue_frame_length
    try:
        new_length = int(queue_length_entry.get())
        queue_frame_length = new_length
        text_box.insert(tk.END, "Cập nhật thành công\n")
        text_box.update()
    except ValueError:
        text_box.insert(tk.END,"Không phải là một số\n")
        text_box.update()

def detectBox(processed_image, image, cmnd_number):
    bounding_box = findBoundingBox(processed_image, cmnd_number)
    if bounding_box is not None:
        x_min, y_min, x_max, y_max = bounding_box
        image = cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
    return image

def findBoundingBox(processed_image, target_text):
    boxes = pytesseract.image_to_boxes(processed_image)
    x_min, y_min, x_max, y_max = float('inf'), float('inf'), 0, 0
    found = False

    for b in boxes.splitlines():
        b = b.split()
        text, x, y, w, h = b[0], int(b[1]), int(b[2]), int(b[3]), int(b[4])
        if text in target_text:
            found = True
            x_min = min(x_min, x)
            y_min = min(y_min, y)
            x_max = max(x_max, w)
            y_max = max(y_max, h)
    
    if found:
        return x_min, y_min, x_max, y_max
    else:
        return None

def crop_corners(image, approx):
    approx = approx.reshape(4, 2)
    rect = np.zeros((4, 2), dtype="float32")
    s = approx.sum(axis=1)
    rect[0] = approx[np.argmin(s)]
    rect[2] = approx[np.argmax(s)]
    diff = np.diff(approx, axis=1)
    rect[1] = approx[np.argmin(diff)]
    rect[3] = approx[np.argmax(diff)]
    (tl, tr, br, bl) = rect
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    maxHeight = max(int(heightA), int(heightB))
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    return warped

def detect_and_draw_rectangles(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)
    
    cv2.imshow('Edges', edges)  # Display edges for debugging

    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        contour_area = cv2.contourArea(contour)
        if 600 <= contour_area:  # Check if contour area is within desired range
            approx = cv2.approxPolyDP(contour, 0.04 * cv2.arcLength(contour, True), True)
            print("Contour found with area:", contour_area)  # Debugging line
            if len(approx) == 4:
                cv2.drawContours(image, [approx], 0, (0, 255, 0), 2)
                print("Detected rectangle:", approx)  # Debugging line
                return approx  # Return the first detected rectangle's approx
            
    #print("No suitable rectangle detected")  # Debugging line
    return None

def update_queue_length_and_detect():
    update_queue_frame_length()
    detectCCCDfromFrame()

def detectCCCDfromFrame():
    cap = VideoCapture()
    cmnd_pattern = re.compile(r'\b\d{12}\b')
    queue_frame = deque(maxlen=queue_frame_length)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        image = frame.copy()
        processed_image = preProcesingImage(image)
        approx = detect_and_draw_rectangles(image)
        if approx is not None:
            print("Cropping using approx:", approx)  # Debugging line
            cropped_image = crop_corners(frame, approx)
            cv2.imshow('Cropped Card', cropped_image)
        else:
            print("Approx is None")  # Debugging line
        
        cmnd_text = pytesseract.image_to_string(processed_image)
        cmnd_numbers = cmnd_pattern.findall(cmnd_text)
        cmnd_numbers = list(set(cmnd_numbers))

        if cmnd_numbers:
            queue_frame.extend(cmnd_numbers)

        counter = Counter(queue_frame)
        most_common_number, count = counter.most_common(1)[0] if counter else (None, 0)
        if count >= (queue_frame_length // 2):
            cmnd_number = most_common_number
        else:
            cmnd_number = "Đang nhận diện..."

        text_info = cap.parse_cmnd(cmnd_number)
        draw_infoCCCD(text_info)
        image = detectBox(processed_image, image, cmnd_number)
        image = draw_cccd_number(image, cmnd_number)
        
        cv2.imshow('Video Capture', image)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            cap.stop()
            break
        elif key == ord('r'):
            queue_frame.clear()
            most_common_cmnd = ""
            output_text = cap.reset()
            text_box.delete(1.0, tk.END)
            text_box.insert(tk.END, output_text)
            text_box.update()

    cap.stop()
    cv2.destroyAllWindows()

root = tk.Tk()
root.title("CCCD Detection")

main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=1)

text_box = tk.Text(main_frame, height=10)
text_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

scrollbar = tk.Scrollbar(main_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
scrollbar.config(command=text_box.yview)

text_box.config(yscrollcommand=scrollbar.set)

queue_length_label = tk.Label(root, text="Queue Length:")
queue_length_label.pack()

queue_length_entry = tk.Entry(root)
queue_length_entry.pack()

update_button = tk.Button(root, text="Update Queue Length", command=update_queue_length_and_detect)
update_button.pack()

root.mainloop()