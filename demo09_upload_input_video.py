import shutil
import os
import tkinter as tk
from tkinter import filedialog

def upload_input_video():
    root = tk.Tk()
    root.withdraw()  # Ẩn cửa sổ chính của tkinter

    file_path = filedialog.askopenfilename(
        title="Chọn file video đầu vào",
        filetypes=[("Video files", "*.mp4;*.mov;*.avi;*.mkv;*.flv;*.webm")]
    )

    if not file_path:
        print("❌ Không chọn file nào. Thoát chương trình.")
        return None

    # Tên file gốc (không có đường dẫn)
    file_name = os.path.basename(file_path)

    # Đường dẫn lưu file vào thư mục hiện tại (cùng cấp với file code)
    destination = os.path.join(os.getcwd(), file_name)

    # Copy file vào thư mục chính
    shutil.copy2(file_path, destination)

    print(f"✅ Đã tải lên file: {file_name} và lưu vào thư mục chính")

    # Trả về tên file vừa upload để xử lý tiếp
    return file_name

if __name__ == "__main__":
    uploaded_file = upload_input_video()
    if uploaded_file:
        print(f"👉 File vừa tải lên: {uploaded_file}")
