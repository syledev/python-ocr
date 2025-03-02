import subprocess
import os

def export_final_video():
    input_file = "final_with_cleaned_sub.mp4"

    # 🔎 Kiểm tra file có tồn tại không
    if not os.path.exists(input_file):
        print(f"❌ Không tìm thấy file {input_file}. Vui lòng đảm bảo đã tạo xong video trước khi xuất.")
        return

    print(f"\n✅ Tìm thấy file {input_file} - Sẵn sàng để xuất.")

    print("\n🔻 Xuất file về máy - Vui lòng chọn thông số:")

    print("📺 Chọn tỷ lệ khung hình:")
    print("1 - 16:9 (Mặc định)")
    print("2 - 9:16 (Dọc)")
    print("3 - 1:1 (Vuông)")
    aspect_choice = input("Nhập lựa chọn (1/2/3): ").strip() or "1"

    print("\n📐 Chọn chất lượng video:")
    print("1 - 480p")
    print("2 - 720p (Mặc định)")
    print("3 - 1080p")
    print("4 - 1440p")
    resolution_choice = input("Nhập lựa chọn (1/2/3/4): ").strip() or "2"

    bitrate = input("\n📊 Nhập bitrate mong muốn (ví dụ: 2M, 5M hoặc bỏ trống để mặc định): ").strip()

    # Map tỷ lệ và độ phân giải
    aspect_ratios = {
        "1": { "480": (854, 480), "720": (1280, 720), "1080": (1920, 1080), "1440": (2560, 1440) },  # 16:9
        "2": { "480": (480, 854), "720": (720, 1280), "1080": (1080, 1920), "1440": (1440, 2560) },  # 9:16
        "3": { "480": (480, 480), "720": (720, 720), "1080": (1080, 1080), "1440": (1440, 1440) },  # 1:1
    }
    resolution_map = {"1": "480", "2": "720", "3": "1080", "4": "1440"}

    # Xác định kích thước cuối cùng
    chosen_res = resolution_map.get(resolution_choice, "720")
    width, height = aspect_ratios.get(aspect_choice, aspect_ratios["1"])[chosen_res]

    # Tên file sau khi export
    output_file = f"final_with_cleaned_sub_{width}x{height}.mp4"

    # Lệnh ffmpeg thực hiện resize + bitrate nếu có
    cmd = [
        "ffmpeg",
        "-i", input_file,
        "-vf", f"scale={width}:{height}"
    ]

    if bitrate:
        cmd += ["-b:v", bitrate]

    cmd += ["-c:a", "aac", "-b:a", "128k", output_file]

    # Chạy lệnh ffmpeg
    subprocess.run(cmd)

    print(f"✅ File đã lưu thành công: {output_file}")

if __name__ == "__main__":
    export_final_video()
