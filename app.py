import os
import streamlit as st
from PIL import Image
from gtts import gTTS
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
import google.generativeai as genai

st.set_page_config(page_title="Tạo Video Affiliate Auto Kịch Bản AI", layout="centered")

st.title("🤖 Tạo Video Affiliate Tự Động 100%")
st.write("Chỉ cần tải ảnh, AI sẽ tự phân tích sản phẩm, viết kịch bản và đọc lời thoại!")

api_key = st.sidebar.text_input("Nhập Google Gemini API Key:", type="password")
st.sidebar.markdown("[👉 Lấy API Key miễn phí tại đây](https://aistudio.google.com/)")

uploaded_images = st.file_uploader(
    "1. Chọn các ảnh sản phẩm (PNG, JPG)", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

if st.button("🚀 Tự Động Tạo Kịch Bản & Video"):
    if not api_key:
        st.error("Vui lòng nhập Gemini API Key ở thanh bên trái!")
    elif not uploaded_images:
        st.error("Vui lòng tải lên ít nhất 1 hình ảnh sản phẩm!")
    else:
        st.info("🤖 AI đang nhìn ảnh và sáng tạo kịch bản tiếp thị...")
        os.makedirs("temp", exist_ok=True)
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-3.6-flash')
        
        first_img = Image.open(uploaded_images[0])
        
        prompt = (
            "Bạn là một chuyên gia tiếp thị liên kết (Affiliate Marketing) trên TikTok/Reels. "
            "Hãy nhìn vào bức ảnh sản phẩm này và viết một kịch bản quảng cáo ngắn gọn, thu hút (khoảng 3-4 câu). "
            "Kịch bản gồm: Giới thiệu điểm nổi bật của sản phẩm và 1 lời kêu gọi bấm vào giỏ hàng để mua. "
            "Chỉ trả về đoạn văn bản kịch bản để đọc, không kèm lời dẫn hay ký tự đặc biệt."
        )
        
        try:
            response = model.generate_content([prompt, first_img])
            script_text = response.text.strip()
            st.success("✨ Kịch bản AI tự tạo:")
            st.write(f'"{script_text}"')
        except Exception as e:
            st.error(f"Lỗi khi AI tạo kịch bản: {e}")
            st.stop()

        st.info("🔊 Đang chuyển kịch bản thành giọng đọc...")
        tts = gTTS(text=script_text, lang='vi', slow=False)
        voice_path = "temp/voice.mp3"
        tts.save(voice_path)
        
        voice_clip = AudioFileClip(voice_path)
        total_duration = voice_clip.duration

        st.info("🎬 Đang ghép video khớp với giọng đọc...")
        num_images = len(uploaded_images)
        duration_per_image = total_duration / num_images
        
        image_clips = []
        target_w, target_h = 1080, 1920

        for idx, img_file in enumerate(uploaded_images):
            img_path = f"temp/img_{idx}.png"
            img = Image.open(img_file)
            
            canvas = Image.new("RGB", (target_w, target_h), (20, 20, 20))
            img.thumbnail((target_w, target_h))
            
            offset = ((target_w - img.width) // 2, (target_h - img.height) // 2)
            canvas.paste(img, offset)
            canvas.save(img_path)

            clip = ImageClip(img_path).set_duration(duration_per_image)
            image_clips.append(clip)

        video_clip = concatenate_videoclips(image_clips, method="compose")
        video_clip = video_clip.set_audio(voice_clip)

        output_path = "output_auto_affiliate.mp4"
        video_clip.write_videofile(
            output_path, 
            fps=24, 
            codec="libx264", 
            audio_codec="aac"
        )

        st.success("🎉 Hoàn tất video!")
        st.video(output_path)
        
        with open(output_path, "rb") as file:
            st.download_button(
                label="📥 Tải Video Về Máy",
                data=file,
                file_name="auto_affiliate_video.mp4",
                mime="video/mp4"
            )
