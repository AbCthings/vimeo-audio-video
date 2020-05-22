#!/usr/bin/env python3
import argparse
import base64
import os
import re
import requests
import subprocess
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--url-list', help='List of URL/filename pairs, delimited by tabs')
args = parser.parse_args()

for line in open(args.url_list):
    output_file, master_json_url = line.rstrip().split('\t')
    print('\n\n\nProcessing %s' % output_file)

    # Extract some stuff
    base_url = master_json_url[:master_json_url.rfind('/', 0, -26) + 1]
    resp = requests.get(master_json_url)
    content = resp.json()

    # Video download here
    heights = [(i, d['height']) for (i, d) in enumerate(content['video'])]
    idx = max(heights, key=lambda x: x[1])[0]
    video = content['video'][idx]
    video_base_url = base_url + video['base_url']
    print('Base url:', video_base_url)

    filenameVideo = 'video_%s.mp4' % video['id']
    print('Saving VIDEO to %s' % filenameVideo)

    video_file = open(filenameVideo, 'wb')

    init_segment = base64.b64decode(video['init_segment'])
    video_file.write(init_segment)

    for segment in tqdm(video['segments']):
        segment_url = video_base_url + segment['url']
        resp = requests.get(segment_url, stream=True)
        if resp.status_code != 200:
            print('not 200!')
            print(resp)
            print(segment_url)
            break
        for chunk in resp:
            video_file.write(chunk)

    video_file.flush()
    video_file.close()

    # Audio download here
    bitrate = [(i, d['bitrate']) for (i, d) in enumerate(content['audio'])]

    print('Bitrate', bitrate)

    idx = max(bitrate, key=lambda x: x[1])[0]
    audio = content['audio'][idx]
    audio_base_url = base_url + audio['base_url']
    print('Base url:', audio_base_url)

    filenameAudio = 'audio_%s.mp4' % audio['id']
    print('Saving AUDIO to %s' % filenameAudio)

    audio_file = open(filenameAudio, 'wb')

    init_segment = base64.b64decode(audio['init_segment'])
    audio_file.write(init_segment)

    for segment in tqdm(audio['segments']):
        segment_url = audio_base_url + segment['url']
        segment_url = re.sub(r'/[a-zA-Z0-9_-]*/\.\./',r'/',segment_url.rstrip())
        resp = requests.get(segment_url, stream=True)
        if resp.status_code != 200:
            print('not 200!')
            print(resp)
            print(segment_url)
            break
        for chunk in resp:
            audio_file.write(chunk)

    audio_file.flush()
    audio_file.close()

    # Combine audio and video here
    print('Combining video and audio...')
    cmd = 'ffmpeg -y -i '
    cmd += filenameAudio
    cmd += ' -i '
    cmd += filenameVideo
    cmd += ' ' + output_file
    subprocess.call(cmd, shell=True)
    print('Mixing Done!')

    # Delete the remaining single audio and video files
    os.remove(filenameAudio)
    os.remove(filenameVideo)
    print("Temporary files removed!")

    # Log the conclusion of the operations
    print("*** VIDEO DOWNLOADED SUCCESSFULLY ***")
