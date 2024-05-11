from queue import Full
#Thư viện OpenCV
import cv2
#Thư viện xử lý số
import numpy as np
#thư viện ORC
import pytesseract
#thư viện xử lý chuỗi
import re
#thư viện bộ nạp
from collections import deque, Counter
#thư viện thời gian
import time
#thư viện phân luồng
import threading
#thư viện Hiển thị text Tiếng Việt
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

    def reset(self):
        # trả về thông tin khai thác được từ số căn cước công dân
        return f"Tỉnh thành: \nThế kỷ: \nNăm sinh: \nID ngẫu nhiên: "

    def parse_cmnd(self, cmnd):
        if len(cmnd) != 12:
            return "Số CMND không hợp lệ. Vui lòng nhập lại."

        province_code = cmnd[:3]
        century = cmnd[3]
        year_of_birth = cmnd[4:6]
        random_id = cmnd[6:]

        # Thư viện mã tỉnh
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
        # thư viện mã thế kỉ
        century_codes = {
            "1": "XX",
            "2": "XXI"
        }

        # thư viện năm sinh
        def year_of_birth_codes(century):
            if century == "XX":
                return "19"
            else:
                return "20"

        # Tra cứu tên tỉnh từ mã tỉnh
        province_name = province_codes.get(province_code, "Không xác định")
        # Tra cứu thế kỷ từ mã thế kỷ
        century_prefix = century_codes.get(century, "Không xác định")
        # Tra cứu năm sinh từ mã năm sinh
        year_of_birth_full = year_of_birth_codes(century_prefix) + year_of_birth
        # trả về thông tin khai thác được từ số căn cước công dân
        return f"Tỉnh thành: {province_name}\nThế kỷ: {century_prefix}\nNăm sinh: {year_of_birth_full}\nID ngẫu nhiên: {random_id}"


pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
queue_frame_lenght = 5
def update_queue_frame_length():
    global queue_frame_lenght
    try:
        new_length = int(queue_length_entry.get())

        queue_frame_lenght = new_length
        text_box.insert(tk.END, "cap nhat thanh cong\n")
        text_box.update()
    except ValueError:
        text_box.insert(tk.END,"khong phai 1 so\n")
        text_box.update()


def run_ocr():
    cap = VideoCapture(0)
    last_queue_cccd = deque(maxlen=queue_frame_lenght)
    text_box.delete(1.0, tk.END)
    # Tạo cửa sổ mới
    # cv2.namedWindow("Output")

    while True:
        ret, image = cap.read()
        if ret:
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            gray_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
            gray_image = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11,
                                               2)

            h, w = gray_image.shape
            boxes = pytesseract.image_to_boxes(gray_image)
            for b in boxes.splitlines():
                b = b.split(' ')
                img = cv2.rectangle(image, (int(b[1]), h - int(b[2])), (int(b[3]), h - int(b[4])), (0, 255, 0), 2)

            cmnd_number = pytesseract.image_to_string(gray_image,
                                                      config="--oem 1 --psm 3 tessedit_char_whitelist=0123456789")
            matches = re.findall(r'\d{12,}', cmnd_number)
            if matches:
                last_match = matches[-1]
                cmnd_number = last_match[-12:] if len(last_match) > 12 else last_match
                last_queue_cccd.append(cmnd_number)

            if len(last_queue_cccd) == queue_frame_lenght:
                counter = Counter(last_queue_cccd)
                most_common_cmnd, _ = counter.most_common(1)[0]
                # print("Số CMND:", most_common_cmnd)
                # Vẽ kết quả lên khung hình
                cv2.putText(image, "CMND number: " + most_common_cmnd, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (0, 255, 0),
                            2, cv2.LINE_AA)
                # Hiển thị kết quả trên cửa sổ mới
                output_text = cap.parse_cmnd(most_common_cmnd)

                captured_output = output_text
                text_box.delete(1.0, tk.END)
                text_box.insert(tk.END, captured_output)
                text_box.update()
                output_image = np.zeros((400, 400, 3), np.uint8)

                # Chuyển đổi hình ảnh sang định dạng PIL
                output_image_pil = Image.fromarray(cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB))

                # Tạo một đối tượng 'draw' để vẽ lên hình ảnh
                draw = ImageDraw.Draw(output_image_pil)

                # Chọn font và kích thước font
                font = ImageFont.truetype("arial.ttf", 34)

                # Vẽ mỗi dòng văn bản
                y = 250
                for line in output_text.split('\n'):
                    draw.text((10, y), line, font=font, fill=(255, 255, 255, 0))
                    y += 40  # Di chuyển xuống cho dòng tiếp theo

                # Chuyển đổi hình ảnh trở lại định dạng OpenCV
                output_image = cv2.cvtColor(np.array(output_image_pil), cv2.COLOR_RGB2BGR)

                # Hiển thị hình ảnh
                cv2.imshow("Output", output_image)#

            cv2.imshow('Webcam', image)
        else:
            print("Không thể đọc ảnh từ webcam!")
            time.sleep(1)  # Tạm dừng 1 giây trước khi thử lại

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            cap.stop()
            root.quit()
            break
        elif key == ord('r'):
            adapter_deque_cccd.clear()
        #reset hiển thị số CCCD
        most_common_cmnd = ""
        #reset hiển thị thông tin CCCD
        # Hiển thị thông tin về số CCCD trên cửa sổ mới
        output_text = cap.reset()
        draw_infoCCCD(output_text)

    cap.cap.release()
    cv2.destroyAllWindows()


root = tk.Tk()
root.title("OCR with OpenCV and Tesseract")

left_frame = tk.Frame(root)
left_frame.pack(side=tk.LEFT, padx=10, pady=10)


run_button = tk.Button(left_frame, text="Start OCR", command=run_ocr)
run_button.pack(anchor=tk.W, padx=5, pady=5)

right_frame = tk.Frame(root)
right_frame.pack(side=tk.RIGHT, padx=10, pady=10)

text_box = tk.Text(right_frame, height=20, width=40)
text_box.pack()

queue_length_entry = tk.Entry(left_frame)
queue_length_entry.insert(tk.END, str(queue_frame_lenght))
queue_length_entry.pack(anchor=tk.W, padx=5, pady=5)

update_button = tk.Button(left_frame, text="Update Queue Length", command=update_queue_frame_length)
update_button.pack(anchor=tk.W, padx=5, pady=5)

root.mainloop()