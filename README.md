# Download segmented videos from Vimeo

## Install prerequisites

Install ffmpeg and Python 3:
* Debian/Ubuntu: `sudo apt install -y ffmpeg python3`
* Mac OS X: `brew install ffmpeg python`

Install Python tqdm module: `sudo python3 -m pip install --upgrade tqdm`

## Instructions to download video
For each video you want to download:
1. Open the page containing the embedded video.
1. Open development console (Chrome: F12).
1. Go to the Network tab.
1. Right click on the `master.json` request, select Copy → Copy link address. An example of how such a URL could look like: `https://178skyfiregce-a.akamaihd.net/exp=1474107106~acl=%2F142089577%2F%2A~hmac=0d9becc441fc5385462d53bf59cf019c0184690862f49b414e9a2f1c5bafbe0d/142089577/video/426274424,426274425,426274423,426274422/master.json?base64_init=1`.

Create a TSV file (can be done e. g. by copy-pasting from Google Sheets), where the first column is output file name (ending with `.mp4`) and the second is this URL to `master.json.

Then run the script, providing the name of this file with names and URLs:
```bash
./vimeo-autio-and-video.py -i names_urls.txt
```

## Acknowledgements
Based on:
* https://gist.github.com/alexeygrigorev/a1bc540925054b71e1a7268e50ad55cd
* https://gist.github.com/brasno/25fe2d30a31b40fe98cc9f55cfb709ab
* https://github.com/AbCthings/vimeo-audio-video
