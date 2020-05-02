'''
@brief download segmented videos from Vimeo
@references https://gist.github.com/alexeygrigorev/a1bc540925054b71e1a7268e50ad55cd
@references https://gist.github.com/brasno/25fe2d30a31b40fe98cc9f55cfb709ab
@instructions 
    1 Open the network tab in the inspector
    2 Find the url of a request to the master.json file
    3 Copy it here
    4 Run the script
'''

# Import section
import requests
import base64
from tqdm import tqdm
import re
import subprocess
import os

# Specify here the master.json file URL
master_json_url = 'https://178skyfiregce-a.akamaihd.net/exp=1474107106~acl=%2F142089577%2F%2A~hmac=0d9becc441fc5385462d53bf59cf019c0184690862f49b414e9a2f1c5bafbe0d/142089577/video/426274424,426274425,426274423,426274422/master.json?base64_init=1'

# Specify here output file name
filenameOutput = 'output.mp4'

# Extract some stuff
base_url = master_json_url[:master_json_url.rfind('/', 0, -26) + 1]
resp = requests.get(master_json_url)
content = resp.json()

# Video download here
heights = [(i, d['height']) for (i, d) in enumerate(content['video'])]
idx, _ = max(heights, key=lambda (_, h): h)
video = content['video'][idx]
video_base_url = base_url + video['base_url']
print 'base url:', video_base_url

filenameVideo = 'video_%s.mp4' % video['id']
print 'saving VIDEO to %s' % filenameVideo

video_file = open(filenameVideo, 'wb')

init_segment = base64.b64decode(video['init_segment'])
video_file.write(init_segment)

for segment in tqdm(video['segments']):
    segment_url = video_base_url + segment['url']
    resp = requests.get(segment_url, stream=True)
    if resp.status_code != 200:
        print 'not 200!'
        print resp
        print segment_url
        break
    for chunk in resp:
        video_file.write(chunk)

video_file.flush()
video_file.close()

# Audio download here
bitrate = [(i, d['bitrate']) for (i, d) in enumerate(content['audio'])]

print 'bitrate', bitrate
 
idx, _ = max(bitrate, key=lambda (_, h): h)
audio = content['audio'][idx]
audio_base_url = base_url + audio['base_url']
print 'base url:', audio_base_url

filenameAudio = 'audio_%s.mp4' % audio['id']
print 'saving AUDIO to %s' % filenameAudio

audio_file = open(filenameAudio, 'wb')

init_segment = base64.b64decode(audio['init_segment'])
audio_file.write(init_segment)

for segment in tqdm(audio['segments']):
    segment_url = audio_base_url + segment['url']
    segment_url = re.sub(r'/[a-zA-Z0-9_-]*/\.\./',r'/',segment_url.rstrip())
    resp = requests.get(segment_url, stream=True)
    if resp.status_code != 200:
        print 'not 200!'
        print resp
        print segment_url
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
cmd += ' -c:v copy -c:a aac '
cmd += filenameOutput
subprocess.call(cmd, shell=True)
print('Mixing Done!')

# Delete the remaining single audio and video files
os.remove(filenameAudio)
os.remove(filenameVideo)
print("Temporary files removed!")

# Log the conclusion of the operations
print("*** VIDEO DOWNLOADED SUCCESSFULLY ***")