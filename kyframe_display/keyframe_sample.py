import streamlit as st
import boto3
import botocore
import json
import os
import tempfile
import shutil
from megfile import smart_open, smart_exists, smart_sync, smart_remove, smart_glob
from deep_translator import GoogleTranslator
import atexit
import sys 
sys.path.append("/data/video_pack")
import samplers
# from samplers import KF_sampler


def cleanup(local_file_path):
    if os.path.exists(local_file_path):
        os.remove(local_file_path)


def get_cache_video(video_path):
    # Determine if the video exists
    video_path = video_path.replace("7m//", "7m/")
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
    
    st.set_page_config(layout="centered", page_icon="🧊", page_title="Howtolink-7M-Dataset-Visulization")
    options_with_children={}

#   ================== 选择数据集和视频 ==================
    st.write('# Select the dataset you want to preview!')
    # 选择框
    selected_child = st.selectbox(
        "Select a dataset",
        ["momentor", "webvid", "internvid", "How2link", "hdvila"],
    )
    
    video_prefix = os.path.join("/data/streamlit_source/keyframe_sapmle/", selected_child)
    
    captions = json.load(open(os.path.join(video_prefix.lower(),"caption.json"),'r'))
    
    value = st.slider("Select a video", 1, 1000, 1)
    

#   ================== 展示视频和caption ==================
    st.write('## Show the video')
    video_path = os.path.join(video_prefix.lower(), f"{value}.mp4")
    st.video(video_path)
    # if selected_child != "internvid":
    st.write(captions[str(value)])
    # st.write(GoogleTranslator(source='en', target='zh-CN').translate(captions[str(value)]))
    
    
#   ================== 展示关键帧 ==================
    # KF_sample 部分因为import 出问题了，需要找时间debug一下
    # Iframes, _ , _ = samplers.KF_sampler(video_path,"I")
    
    # st.write('## Show the IFrames:')
    # for i in Iframes:
    #     st.image(i)

    # st.write('## Show the PFrames:')
    
    # Pframes, _ , _ = samplers.KF_sampler(video_path,"P")
    # for i in Pframes:
    #     st.image(i)

if __name__ == '__main__':
    main()
    