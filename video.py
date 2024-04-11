import streamlit as st
import boto3
import botocore
import os
import tempfile
import shutil
from megfile import smart_open, smart_exists, smart_sync, smart_remove, smart_glob
import atexit


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





def main():
    st.title("Video Test Page")
    video_path = "s3://kanelin/interlink7m/Howto-Interlink7M_subset_w_all_clips_train/--FsPMKkt9c/clip_3.mp4"
    local_video_path = get_cache_video(video_path)
    # local_video_path="test.mp4"
    # 在Streamlit中展示本地视频文件
    st.video(local_video_path)

    # st.image("zebra.jpg")

    # 删除本地视频文件
    atexit.register(cleanup, local_video_path)

if __name__ == '__main__':
    main()
    # video_file_path = "test.mp4"

    # # 获取视频文件的filehead，这里指定读取前10个字节
    # file_head = get_file_head(video_file_path)
    # print(file_head)

