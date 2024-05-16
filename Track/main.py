#  The code is for visualizing the tracking result from the json file
import streamlit as st
import boto3
import cv2
import botocore
import json
import os
from megfile import smart_open, smart_exists, smart_sync, smart_remove, smart_glob
import sys 
import numpy as np
sys.path.append("/data/video_pack")
# from samplers import KF_sampler

def prepareBT(jsonFilePath):
    image_track_pair = {}
    display_list = []
    meta_inofs = json.load(open(jsonFilePath))
    
    for video in meta_inofs:
        for clip in video['clips']:
            for frame_id in clip['track'].keys():
                image_track_pair[frame_id] = clip['track'][frame_id]
                for track_id in image_track_pair[frame_id].keys():
                    iamge_name = image_track_pair[frame_id][track_id]['file']
                    image_track_pair[frame_id][track_id]['file'] = os.path.join(clip['clip_path'], iamge_name)
    
    for key in image_track_pair.keys():
        display_list.append(image_track_pair[key])
    
    print("Process json files successfully!")
    print("loaded json file successfully!")
    
    return display_list

def prepareGRiT(jsonFilePath):
    image_track_pair = {} 
    display_list = []
    meta_inofs = json.load(open(jsonFilePath))
    
    for video in meta_inofs:
        for clip in video['clips']:
            for frame_id in clip['track'].keys():
                frame_dict = {}
                for track_id in range(len(clip['track'][frame_id]['caption'])):
                    file = os.path.join(clip['clip_path'], clip['track'][frame_id]['frame_name'])
                    caption = clip['track'][frame_id]['caption'][track_id]
                    tlbr = clip['track'][frame_id]['dets'][track_id]
                    frame_dict[str(track_id)] = {'file': file, 'caption': caption, 'tlwh': tlbr}
                image_track_pair[frame_id] = frame_dict

    for key in image_track_pair.keys():
        display_list.append(image_track_pair[key])

    print("Process json files successfully!")
    print("loaded json file successfully!")
    
    return display_list

def prepareRaw(jsonFilePath):
    image_track_pair = {} 
    display_list = []

    meta_inofs = json.load(open(jsonFilePath))

    for frame_id in meta_inofs.keys():
        frame_dict = {}
        for track_id in range(len(meta_inofs[frame_id]['caption'])):
            file = meta_inofs[frame_id]['file']
            caption = meta_inofs[frame_id]['caption'][track_id]
            tlbr = [ i/(720.0/455.0) for i in meta_inofs[frame_id]['dets'][track_id]]
            frame_dict[str(track_id)] = {'file': file, 'caption': caption, 'tlwh': tlbr}
        image_track_pair[frame_id] = frame_dict

    for key in image_track_pair.keys():
        display_list.append(image_track_pair[key])
    
    return display_list

def pil_to_cv2(image_pil):
    # Convert PIL image to numpy array
    image_np = np.array(image_pil)
    
    # Convert RGB to BGR (OpenCV uses BGR color order)
    image_cv2 = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
    
    return image_cv2

def load_image(image_path):
    
    from PIL import Image
    import megfile
    from io import BytesIO
    import os

    os.environ["AWS_PROFILE"] = "tos"
    os.environ["OSS_ENDPOINT"] = "http://tos-s3-cn-shanghai.ivolces.com"
    
    if 's3://' in image_path:
        with megfile.smart_open(image_path, "rb") as f:
            bytes_data = f.read()
        image = Image.open(BytesIO(bytes_data), "r").convert('RGB')
    else:
        image = Image.open(image_path).convert('RGB')
        
    return image

def draw(img, tlwh, mode ,color=(0, 255, 0), thickness=2):
    img = pil_to_cv2(img)
    t, l, w, h = map(int, tlwh)
    x1, y1 = t, l
    if mode == "tlwh":
        x2, y2 = t + w, l + h
    elif mode == "tlbr":
        x2, y2 = w, h
    img = cv2.rectangle(img, (x1, y1), (x2, y2), color, thickness)
    return img


def main():
    # 1. 可视化直接从 grit 得到的结果
    # jsonFilePath = "/data/merlin_track/draft/5_16/raw_grit.json"
    # display_list = prepareRaw(jsonFilePath)

    # 2. 可视化从 grit 提取得到的结果
    # jsonFilePath = "/data/merlin_track/draft/5_16/extract_from_grit.json"
    # display_list = prepareGRiT(jsonFilePath)

    # 3. 可视化从 bt 提取得到的结果
    jsonFilePath = "/data/merlin_track/draft/5_16/byte_track.json"
    display_list = prepareBT(jsonFilePath)
    

    st.set_page_config(layout="centered", page_icon="🧊", page_title="Merlin-Track")

#   ================== 输入要可视化的 json 文件的路径 并准备数据 ==================
    st.write('# Now you can visualize the tracking result')
    # 选择框

#   ================== 选择 bbox 框的表示方式和视频的id ==================
    st.write('## Show the bounding box')
    display_mode = st.selectbox("Select the box mode", ["tlbr", "tlwh"], index=0)
    shown_iamge_id  = st.slider("Select a video", 1, 100, 1)
    track_id = st.selectbox("Select the track id u want to preview", list(display_list[shown_iamge_id].keys()), index=0)
    
    image_path = display_list[shown_iamge_id][str(track_id)]['file']
    bbox = display_list[shown_iamge_id][str(track_id)]['tlwh']
    caption = display_list[shown_iamge_id][str(track_id)]['caption']
    image = draw(load_image(image_path), bbox, display_mode)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    st.image(image, caption=caption, use_column_width=True)
    
    st.write("The bbox is: ", bbox)


if __name__ == '__main__':
    main()