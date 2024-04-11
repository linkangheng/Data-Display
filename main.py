import streamlit as st
from rembg import remove
from PIL import Image
from io import BytesIO
import base64
from megfile import smart_open, smart_exists, smart_sync, smart_remove, smart_glob
import atexit



MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Download the fixed image
def convert_image(img):
    buf = BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()
    return byte_im

def cleanup(local_file_path):
    if os.path.exists(local_file_path):
        os.remove(local_file_path)

def get_cache_video(video_path):
    # Determine if the video exists
    if not smart_exists(video_path):
        error_message = f"Video file not found: {video_path}"
        print(error_message)
        return 

    # Caching the video
    with smart_open(video_path, 'rb') as file_obj:
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
            shutil.copyfileobj(file_obj, temp_file)
            cache_video_path = temp_file.name
            
    return cache_video_path

def fix_images(address_list):
    num_images = len(address_list)
    for i in range(num_images):
        image = Image.open(address_list[i])
        st.write(f"Image {i + 1}: Original Image :camera:")
        st.image(image)

        fixed = remove(image)  # 假设remove函数用于处理图像
        st.write(f"Image {i + 1}: Fixed Image :wrench:")
        st.image(fixed)

        st.markdown("\n")

def show_clip(video_path):
    local_video_path = get_cache_video(video_path)
    if local_video_path is None:
        return
    st.video(local_video_path)
    atexit.register(cleanup, local_video_path)

def main():
    st.set_page_config(layout="wide", page_title="Image Background Remover")

    st.write("# Show the datasets of processed images")
    st.write(
        ":dog: Try uploading an image to watch the background magically removed. Full quality images can be downloaded from the sidebar. This code is open source and available [here](https://github.com/tyler-simons/BackgroundRemoval) on GitHub. Special thanks to the [rembg library](https://github.com/danielgatis/rembg) :grin:"
    )
    # 侧边栏选择视频
    st.sidebar.write("## Choose a video :movie_camera:")
    video_path = st.sidebar.text_input("Enter the path to the video file", value="zebra.mp4")
    st.sidebar.write("## Process the video :gear:")
    show_clip(video_path)
    ################## Show the video clip################# 
    st.write("# The cliped video will be shown here")
    
    local_video_path = get_cache_video(video_path)
    if local_video_path is None:
        return
    st.video(local_video_path)
    atexit.register(cleanup, local_video_path)
    
    
    st.sidebar.write("## Upload and download :gear:")

    col1, col2 = st.columns(2)
    my_upload = st.sidebar.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

    if my_upload is not None:
        if my_upload.size > MAX_FILE_SIZE:
            st.error("The uploaded file is too large. Please upload an image smaller than 5MB.")
        else:
            fix_image(upload=my_upload)
    else:
        fix_image("./zebra.jpg")

