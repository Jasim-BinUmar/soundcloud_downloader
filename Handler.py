
import requests as req
import urllib.request
import re
import os
import json
import sys
import shutil
import progressbar
# from PyQt5.QtGui import *

class Handler:

	def getClienId(self):
		try:
		  data = req.get("https://m.soundcloud.com")
		  client_id = re.search(r'clientId":"(.*?)",', data.text).group(1)
		  return client_id
		except:
		  print("An exception occurred")
		  sys.exit()

	def getMp3Track(self,url,bara,QApplication):
		client_id = self.getClienId()
		respa = req.get("https://soundcloud.com" + url.split("soundcloud.com")[-1].split("?")[0] if "soundcloud.com" in url else url)
		respa_text = respa.text

		match = re.search(r'<script>window\.__sc_hydration\s*=\s*(\[.*?\]);</script>', respa_text, re.DOTALL)
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
					resulta = {'data': [track_data]}
				else:
					raise ValueError("Track data not found in hydration")
			except:
				match = None

		if not match or 'resulta' not in locals():
			respa = req.get("https://w.soundcloud.com/player/?url="+url)
			respa_text = respa.text.encode('utf-8').decode('ascii', 'ignore')
			match = re.search(r'}}\)},\[(.*?)}]}]', respa_text)
			if not match:
				print("Error: Could not find track data in SoundCloud response")
				sys.exit(1)
			resulta_text = match.group(1) + "}]}"
			resulta = json.loads(resulta_text)

		stream_url = resulta['data'][0]['media']['transcodings'][0]['url']
		if '?' in stream_url:
			stream_url += "&client_id=" + client_id
		else:
			stream_url += "?client_id=" + client_id
		print("Stream URL:", stream_url)
		title = resulta['data'][0]['title']
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
		bara.setValue(10)
		QApplication.processEvents()
		cmd = f'ffmpeg -i "{hls_url}" -c copy -bsf:a aac_adtstoasc "{output_file}" -y -loglevel error'
		result = os.system(cmd)
		if result != 0:
			bara.setValue(50)
			QApplication.processEvents()
			cmd = f'ffmpeg -i "{hls_url}" -c:a libmp3lame -b:a 192k "{output_file}" -y -loglevel error'
			result = os.system(cmd)
			if result != 0:
				print("Error: Download failed")
				sys.exit(1)
		bara.setValue(100)
		QApplication.processEvents()
		print(f"Successfully downloaded: {output_file}")



	