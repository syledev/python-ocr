import os
import re
import time
import google.generativeai as genai

# Configure with your valid API key
genai.configure(api_key="AIzaSyCSdeDMl_G_5x8vOVbJOEbffdTQPyFb8UM")

# Initialize model
model = genai.GenerativeModel("gemini-1.5-pro")

def translate_text(block):
    max_retries = 5  # Increased retries
    retry_delay = 5  # Increased initial delay

    for attempt in range(max_retries):
        try:
            prompt = f"""
Dịch đoạn phụ đề sau sang tiếng Việt. Giữ nguyên số thứ tự, thời gian và format SRT:
{block}
"""
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            if attempt < max_retries - 1:  # Don't sleep on last attempt
                sleep_time = retry_delay * (2 ** attempt)  # Exponential backoff
                print(f"Retry attempt {attempt + 1}/{max_retries}. Waiting {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                print(f"Failed after {max_retries} attempts. Error: {str(e)}")
                return block  # Return original text if all retries fail

# Read original SRT file
with open("subtitles.srt", "r", encoding="utf-8") as file:
    srt_content = file.read()

# Split subtitles into blocks
srt_blocks = re.split(r'\n\s*\n', srt_content.strip())

# Process and translate each block
translated_blocks = []
for i, block in enumerate(srt_blocks, 1):
    print(f"Translating block {i}/{len(srt_blocks)}...")
    translated_block = translate_text(block)
    translated_blocks.append(translated_block)
    time.sleep(2)  # Increased delay between requests

# Write to new SRT file
translated_srt_content = "\n\n".join(translated_blocks)
with open("translated_subtitles.srt", "w", encoding="utf-8") as out_file:
    out_file.write(translated_srt_content)

print(" Đã dịch và lưu ra translated_subtitles.srt")