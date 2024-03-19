import boto3
import json
import streamlit as st
import os
from pathlib import Path

AWS_ACCESS_KEY = st.secrets["AWS_ACCESS_KEY"]
AWS_SECRET_KEY = st.secrets["AWS_SECRET_KEY"]
BUCKET_NAME = "qu-nist"

# get the last updated json from data/last_updated.json locally
def get_last_updated_local():
    with open('data/last_updated.json', 'r') as f:
        last_updated = json.load(f)
    return last_updated

# get the last updated json from s3
def get_last_updated_s3():
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
    last_updated = {"videos":{}, "slides":{}, 'transcripts':{}}
    for obj in s3.list_objects_v2(Bucket=BUCKET_NAME)['Contents']:
        # if the file is a video, store the file name and last modified date in a dictionary and return it
        if obj['Key'].split('.')[-1] == 'mp4':
            last_updated["videos"][obj['Key'].split('/')[-1]] = obj['LastModified']
        elif obj['Key'].split('.')[-1] == 'pdf':
            last_updated["slides"][obj['Key'].split('/')[-1]] = obj['LastModified']
        elif obj['Key'].split('.')[-1] == 'txt':
            last_updated["transcripts"][obj['Key'].split('/')[-1]] = obj['LastModified']

    return last_updated

    
def fetch_updated_files():
    # with st.write("Getting latest content...")
    Path("./data/videos").mkdir(parents=True, exist_ok=True)
    Path("./data/slides").mkdir(parents=True, exist_ok=True)
    Path("./data/transcripts").mkdir(parents=True, exist_ok=True)
    local_files = get_last_updated_local()
    s3_files = get_last_updated_s3()
    print(local_files, s3_files)
    # iterate over the vidoes and download the updated videos
    for video in s3_files["videos"]:
        if video not in local_files["videos"] or s3_files["videos"][video].strftime("%Y-%m-%d %H:%M:%S") != local_files["videos"][video]:
            # delete the old video
            if video in local_files["videos"]:
                os.remove("data/videos/"+video)
            # download the new video
            s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
            s3.download_file(BUCKET_NAME, "videos/"+video, "data/videos/"+video)
            local_files["videos"][video] = s3_files["videos"][video].strftime("%Y-%m-%d %H:%M:%S")
    
    # delete the local videos that are not present in the s3_file
    for video in local_files["videos"]:
        if video not in s3_files["videos"] and os.path.exists("data/videos/"+video):
            os.remove("data/videos/"+video)
            del local_files["videos"][video]

    # iterate over the slides and download the updated slides
    for slide in s3_files["slides"]:
        if slide not in local_files["slides"] or s3_files["slides"][slide].strftime("%Y-%m-%d %H:%M:%S") != local_files["slides"][slide]:
            # delete the old slide
            if slide in local_files["slides"]:
                os.remove("data/slides/"+slide)
            # download the new slide
            s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
            s3.download_file(BUCKET_NAME, "slides/"+slide, "data/slides/"+slide)
            local_files["slides"][slide] = s3_files["slides"][slide].strftime("%Y-%m-%d %H:%M:%S")

    # delete the local slides that are not present in the s3_file
    for slide in local_files["slides"]:
        if slide not in s3_files["slides"] and os.path.exists("data/slides/"+slide):
            os.remove("data/slides/"+slide)
            del local_files["slides"][slide]

    # iterate over teh transcripts and download the updated transcripts
    for transcript in s3_files["transcripts"]:
        if transcript not in local_files["transcripts"] or s3_files["transcripts"][transcript].strftime("%Y-%m-%d %H:%M:%S") != local_files["transcripts"][transcript]:
            # delete the old transcript
            if transcript in local_files["transcripts"]:
                os.remove("data/transcripts/"+transcript)
            # download the new transcript
            s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
            s3.download_file(BUCKET_NAME, "transcripts/"+transcript, "data/transcripts/"+transcript)
            local_files["transcripts"][transcript] = s3_files["transcripts"][transcript].strftime("%Y-%m-%d %H:%M:%S")

    # delete the local transcripts that are not present in the s3_file
    for transcript in local_files["transcripts"]:
        if transcript not in s3_files["transcripts"] and os.path.exists("data/transcripts/"+transcript):
            os.remove("data/transcripts/"+transcript)
            del local_files["transcripts"][transcript]
    
    # update the last updated json
    with open('data/last_updated.json', 'w') as f:
        json.dump(local_files, f)

