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

def sort_key(s):
    return int(s.split("_")[1].replace(".jpg", ""))

def main():
    import json
    data = json.load(open('/home/kanghenglin/merlin_track/test.json'))    
    st.set_page_config(layout="centered", page_icon="🧊", page_title="Howtolink-7M-Dataset-Visulization")
    options_with_children={}
    for i in range(len(data)):
        video_id = data[i]['video_path'].split("/")[-2]
        video_clips = [video_id + " clip: "+data[i]['clips'][j]['clip_id'] for j in range(len(data[i]['clips']))]
        options_with_children[video_id] = video_clips

    st.write('# Please select an clip')
    selected_option = st.sidebar.selectbox('Select a video you want to preview!', list(options_with_children.keys()))

    selected_child = st.selectbox('', options_with_children[selected_option], index=0, format_func=lambda x: f'Clip ID: {x.split()[-1]}')

    video_id = selected_child.split()[0]
    clip_id = "clip_"+str(selected_child.split()[-1])
    st.write('## Show the clip')
    video_path = os.path.join('s3://kanelin/interlink7m//Howto-Interlink7M_subset_w_all_clips_train',video_id,clip_id+".mp4")
    frames_path = os.listdir(os.path.join('/data/howtolink/vis',video_id,clip_id))
    
    # 展示视频
    cache_video_path = get_cache_video(video_path)
    st.video(cache_video_path)
    st.write('# Frames:')
    # 展示图片
    frames_path = sorted(frames_path,key=sort_key)

    for i in range(len(frames_path)):
        st.write("### "+frames_path[i].split(".")[0])
        st.image(os.path.join('/data/howtolink/vis',video_id,clip_id,frames_path[i]),channels="BGR")
    # 清理缓存
    atexit.register(cleanup, cache_video_path)


if __name__ == '__main__':
    main()