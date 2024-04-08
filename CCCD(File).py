import re
import cv2
import pytesseract
import numpy as np

pytesseract.pytesseract.tesseract_cmd = r'D:\Program Files\Tesseract-OCR\tesseract.exe'

# Đọc ảnh từ tệp
image_path = "cccd1.jpg"
image = cv2.imread(image_path)

# Kiểm tra xem ảnh đã được đọc thành công chưa
if image is not None:
    # Tăng độ phân giải
    h, w = image.shape[:2]
    resize_image = cv2.resize(image, (2 * w, 2 * h), interpolation=cv2.INTER_LINEAR)
    cv2.imwrite('resize.jpg', resize_image)

    # Chuyển ảnh sang độ xám
    gray_image = cv2.cvtColor(resize_image, cv2.COLOR_BGR2GRAY)
    cv2.imwrite('img_gray.jpg', gray_image)

    # Làm mờ ảnh
    gaussian_image = cv2.GaussianBlur(gray_image, (3, 3), 0)
    cv2.imwrite('blur.jpg', gaussian_image)

    #lọc nhiễu

    # Thay đổi ngưỡng
    bin_image = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    cv2.imwrite('threshold.jpg', bin_image)

    # Su dung ham Canny để phát hiện các cạnh trong ảnh
    edges = cv2.Canny(bin_image, 30, 100)

    # Tìm contours trong ảnh
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Duyệt qua từng contour
    for contour in contours:
        # Tính hình chữ nhật bao quanh contour
        x, y, w, h = cv2.boundingRect(contour)

        # Kiểm tra xem hình chữ nhật có phải là thẻ CCCD không
        aspect_ratio = w / h
        if 1.5 < aspect_ratio < 1.7:  # Giả sử thẻ CCCD có tỷ lệ cạnh là 1.6
            # Vẽ hình chữ nhật lên ảnh gốc
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Lưu ảnh với hình chữ nhật
    cv2.imwrite('rectangle.jpg', image)

    # Sử dụng thư viện pytesseract để nhận dạng số CMND
    cmnd_number = pytesseract.image_to_string(bin_image, config="--oem 1 --psm 6 tessedit_char_whitelist=0123456789")

    # Tìm kiếm số căn cước công dân bằng regex
    matches = re.findall(r'\d{12,}', cmnd_number)

    # Nếu tìm thấy ít nhất một chuỗi con
    if matches:
        last_match = matches[-1]
        if len(last_match) > 12:
            cmnd_number = last_match[-12:]
        else:
            cmnd_number = last_match
    else:
        cmnd_number = "Không tìm thấy số căn cước công dân"

    # Hiển thị số CMND
    print("Số CMND:", cmnd_number)
else:
    print("Không thể đọc ảnh từ tệp!")
