import pysrt
import subprocess
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ColorClip
from moviepy.config import change_settings

change_settings({"IMAGEMAGICK_BINARY": r"C:\\Program Files\\ImageMagick-7.1.1-Q16\\magick.exe"})

def srt_time_to_seconds(time_obj):
    """Chuyển datetime.time thành tổng số giây"""
    return time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second + time_obj.microsecond / 1e6

def adjust_audio_to_video(audio_file, video_file, output_audio):
    """Điều chỉnh tốc độ âm thanh để khớp với video"""
    video = VideoFileClip(video_file)
    video_duration = video.duration

    # Lấy thời lượng audio bằng FFmpeg
    result = subprocess.run(
        ["ffprobe", "-i", audio_file, "-show_entries", "format=duration", "-v", "quiet", "-of", "csv=p=0"],
        capture_output=True, text=True
    )
    audio_duration = float(result.stdout.strip())

    if video_duration <= 0 or audio_duration <= 0:
        print("❌ Lỗi: Video hoặc Audio có độ dài không hợp lệ!")
        return None

    # ✅ Công thức chuẩn: speed_factor = audio_duration / video_duration
    speed_factor = audio_duration / video_duration  
    print(f"📊 Video: {video_duration:.2f}s, Audio: {audio_duration:.2f}s, Hệ số: {speed_factor:.3f}")

    # Điều chỉnh tốc độ bằng FFmpeg
    atempo_filter = []
    while speed_factor > 2.0:
        atempo_filter.append("atempo=2.0")
        speed_factor /= 2
    while speed_factor < 0.5:
        atempo_filter.append("atempo=0.5")
        speed_factor *= 2
    atempo_filter.append(f"atempo={speed_factor:.3f}")
    atempo_filter = ",".join(atempo_filter)

    subprocess.run(["ffmpeg", "-i", audio_file, "-filter:a", atempo_filter, "-vn", output_audio, "-y"])
    print(f"✅ Đã điều chỉnh âm thanh: {output_audio}")

    return 1 / speed_factor  # Lấy nghịch đảo để áp dụng cho phụ đề

def adjust_srt_to_audio(srt_file, output_srt, speed_factor, video_duration):
    """Chỉnh sửa phụ đề để khớp với tốc độ âm thanh đã điều chỉnh"""
    subs = pysrt.open(srt_file, encoding="utf-8")

    # 🛠 Tính tổng thời lượng phụ đề gốc
    original_end = srt_time_to_seconds(subs[-1].end.to_time())

    # 🎯 Hệ số mới để đưa phụ đề lên đúng thời gian video
    correction_factor = video_duration / original_end

    print(f"🔄 Hệ số speed_factor gốc: {speed_factor:.3f}")
    print(f"📏 Thời lượng phụ đề trước: {original_end:.2f}s")
    print(f"🎯 Hệ số điều chỉnh chính xác: {correction_factor:.3f}")

    for sub in subs:
        original_start = srt_time_to_seconds(sub.start.to_time())
        original_end = srt_time_to_seconds(sub.end.to_time())

        # ✅ Nhân với correction_factor để kéo phụ đề đúng 59s
        new_start = original_start * correction_factor
        new_end = original_end * correction_factor

        sub.start = pysrt.SubRipTime(seconds=new_start)
        sub.end = pysrt.SubRipTime(seconds=new_end)

    subs.save(output_srt, encoding="utf-8")
    print(f"✅ Đã điều chỉnh phụ đề: {output_srt} (Hệ số: {correction_factor:.3f})")

def process_video(video_file, audio_file, srt_file, output_video):
    """Ghép audio đã chỉnh và phụ đề vào video"""
    video = VideoFileClip(video_file)
    audio = AudioFileClip(audio_file)
    w, h = video.size

    video = video.set_audio(audio)

    # Tạo thanh nền đen phía dưới để hiển thị phụ đề
    black_bar = ColorClip(size=(w, 100), color=(0, 0, 0), duration=video.duration)
    black_bar = black_bar.set_position(("center", h - 100))

    # Xử lý phụ đề
    subs = pysrt.open(srt_file, encoding="utf-8")
    sub_clips = []
    for sub in subs:
        start_time = srt_time_to_seconds(sub.start.to_time())
        duration = srt_time_to_seconds(sub.end.to_time()) - start_time

        txt_clip = TextClip(
            sub.text, fontsize=35, color='yellow', font="Liberation-Sans",
            size=(w - 100, None), method='caption', bg_color="black"
        ).set_start(start_time).set_duration(duration).set_position(('center', h - 120))

        sub_clips.append(txt_clip)

    final_clip = CompositeVideoClip([video, black_bar] + sub_clips)
    final_clip.write_videofile(output_video, fps=24, codec="libx264", audio_codec="aac")
    print(f"🎬 Video hoàn tất: {output_video}")

def create_synchronized_files(audio_file, video_file, srt_file, output_audio, output_srt):
    """Tạo file âm thanh và phụ đề đã đồng bộ với video"""
    speed_factor = adjust_audio_to_video(audio_file, video_file, output_audio)
    
    if speed_factor:
        video = VideoFileClip(video_file)  # ✅ Lấy thời lượng video
        adjust_srt_to_audio(srt_file, output_srt, speed_factor, video.duration)  # ✅ Truyền thêm video_duration
        print(f"✅ Đã tạo xong file âm thanh và phụ đề đồng bộ.")
        return True
    return False

if __name__ == "__main__":
    if create_synchronized_files(
        audio_file="final_audio.mp3", 
        video_file="input.mp4", 
        srt_file="translated_subtitles.srt", 
        output_audio="adjusted_audio.mp3", 
        output_srt="adjusted_subtitles.srt"
        
    ):
        process_video("input.mp4", "adjusted_audio.mp3", "adjusted_subtitles.srt", "final_with_cleaned_sub.mp4")
