import requests as req
import re
import os
import json
import unicodedata
import logging
import subprocess

logger = logging.getLogger(__name__)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}


def get_client_id(session=None):
    try:
        if session is None:
            session = req.Session()
        data = session.get("https://m.soundcloud.com", headers=HEADERS)
        client_id = re.search(r'clientId":"(.*?)",', data.text).group(1)
        return client_id, session
    except Exception as e:
        raise Exception(f"Failed to get client ID: {str(e)}")


def download_track(url):
    downloads_dir = "downloads"
    if not os.path.exists(downloads_dir):
        os.makedirs(downloads_dir)
    
    session = req.Session()
    client_id, session = get_client_id(session)
    clean_url = url.split("soundcloud.com")[-1].split("?")[0] if "soundcloud.com" in url else url
    respa = session.get("https://soundcloud.com" + clean_url, headers=HEADERS)
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
        respa = session.get("https://w.soundcloud.com/player/?url="+url, headers=HEADERS)
        respa_text = respa.text.encode('utf-8').decode('ascii', 'ignore')
        match = re.search(r'}}\)},\[(.*?)}]}]', respa_text)
        if not match:
            raise Exception("Could not find track data in SoundCloud response")
        resulta_text = match.group(1) + "}]}"
        resulta = json.loads(resulta_text)

    stream_url = resulta['data'][0]['media']['transcodings'][0]['url']
    if '?' in stream_url:
        stream_url += "&client_id=" + client_id
    else:
        stream_url += "?client_id=" + client_id
    
    title = resulta['data'][0]['title']
    try:
        title = title.encode('latin1').decode('utf-8')
    except:
        pass

    api_headers = HEADERS.copy()
    api_headers['Accept'] = 'application/json, text/javascript, */*; q=0.01'
    api_headers['Referer'] = url if url.startswith('http') else f'https://soundcloud.com{clean_url}'
    api_headers['X-Requested-With'] = 'XMLHttpRequest'
    api_headers['Origin'] = 'https://soundcloud.com'
    
    stream_resp = session.get(stream_url, headers=api_headers)
    if stream_resp.status_code != 200:
        logger.error(f"Stream manifest request failed. Status: {stream_resp.status_code}, Response: {stream_resp.text[:200]}")
        raise Exception(f"Could not get stream manifest. Status code: {stream_resp.status_code}")
    stream_resp_data = stream_resp.json()
    if 'url' not in stream_resp_data:
        raise Exception("No stream URL in response")
    hls_url = stream_resp_data['url']
    
    title_safe = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', title)
    title_safe = title_safe.strip()
    
    try:
        title_safe = unicodedata.normalize('NFKD', title_safe).encode('ascii', 'ignore').decode('ascii')
    except:
        pass
    
    title_safe = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', title_safe)
    title_safe = title_safe.strip()
    
    if not title_safe or len(title_safe.strip()) == 0:
        title_safe = "soundcloud_track"
    
    output_file = os.path.join(downloads_dir, title_safe + ".mp3")
    
    logger.info(f"Starting download: {title_safe}")
    logger.info(f"Output file: {output_file}")
    logger.info(f"HLS URL: {hls_url[:100]}...")
    
    logger.info(f"Running ffmpeg command...")
    try:
        result = subprocess.run(
            ['ffmpeg', '-i', hls_url, '-c:a', 'libmp3lame', '-b:a', '192k', output_file, '-y', '-loglevel', 'error', '-nostdin'],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode != 0:
            error_msg = f"FFmpeg download failed with exit code {result.returncode}"
            if result.stderr:
                error_msg += f": {result.stderr}"
            logger.error(error_msg)
            raise Exception(error_msg)
    except subprocess.TimeoutExpired:
        error_msg = "FFmpeg download timed out after 5 minutes"
        logger.error(error_msg)
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"FFmpeg execution error: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)
    
    if not os.path.exists(output_file):
        error_msg = f"Downloaded file not found at {output_file}"
        logger.error(error_msg)
        raise Exception(error_msg)
    
    logger.info(f"Download completed successfully: {output_file}")
    return output_file

