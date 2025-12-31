
import requests as req
import urllib.request
import re
import os
import json
import sys
import shutil
import progressbar

def getClienId():
	try:
	  data = req.get("https://m.soundcloud.com")
	  client_id = re.search(r'clientId":"(.*?)",', data.text).group(1)
	  return client_id
	except:
	  print("An exception occurred")
	  sys.exit()


print("Welcome to Python Soundcloud downloader using stream/hls (chunk not progressive links)")
if len(sys.argv) > 1:
    track_link = sys.argv[1]
else:
    track_link = input("Please give a track url:")

client_id = getClienId()
respo = req.get("https://soundcloud.com" + track_link.split("soundcloud.com")[-1].split("?")[0] if "soundcloud.com" in track_link else track_link)
respo_text = respo.text

match = re.search(r'<script>window\.__sc_hydration\s*=\s*(\[.*?\]);</script>', respo_text, re.DOTALL)
if match:
    try:
        hydration_data = json.loads(match.group(1))
        track_data = None
        for item in hydration_data:
            if isinstance(item, dict) and 'data' in item:
                data = item['data']
                if isinstance(data, dict) and 'media' in data and 'transcodings' in data.get('media', {}):
                    track_data = data
                    break
        if track_data:
            _result = {'data': [track_data]}
        else:
            raise ValueError("Track data not found in hydration")
    except:
        match = None

if not match or '_result' not in locals():
    respo = req.get("https://w.soundcloud.com/player/?url="+track_link)
    respo_text = respo.text.encode('utf-8').decode('ascii', 'ignore')
    match = re.search(r'}}\)},\[(.*?)}]}]', respo_text)
    if not match:
        print("Error: Could not find track data in SoundCloud response")
        sys.exit(1)
    _result_text = match.group(1) + "}]}"
    _result = json.loads(_result_text)

stream_url = _result['data'][0]['media']['transcodings'][0]['url']
if '?' in stream_url:
    stream_url += "&client_id=" + client_id
else:
    stream_url += "?client_id=" + client_id
print("Stream URL:", stream_url)
title = _result['data'][0]['title']
try:
    title = title.encode('latin1').decode('utf-8')
except:
    pass
print("Title:", title)
stream_resp = req.get(stream_url)
if stream_resp.status_code != 200:
    print(f"Error: Could not get stream manifest. Status code: {stream_resp.status_code}")
    sys.exit(1)
stream_resp_data = stream_resp.json()
if 'url' not in stream_resp_data:
    print("Error: No stream URL in response")
    sys.exit(1)
hls_url = stream_resp_data['url']
print("HLS URL:", hls_url)
title_safe = re.sub(r'[<>:"/\\|?*]', '', title)
title_safe = title_safe.strip()
if not title_safe:
    title_safe = "soundcloud_track"
output_file = title_safe + ".mp3"
print(f"Downloading to: {output_file}")
print("This may take a while...")
cmd = f'ffmpeg -i "{hls_url}" -c copy -bsf:a aac_adtstoasc "{output_file}" -y'
result = os.system(cmd)
if result != 0:
    print("Error: ffmpeg download failed. Trying alternative method...")
    cmd = f'ffmpeg -i "{hls_url}" -c:a libmp3lame -b:a 192k "{output_file}" -y'
    result = os.system(cmd)
    if result != 0:
        print("Error: Download failed")
        sys.exit(1)
print(f"Successfully downloaded: {output_file}")


	