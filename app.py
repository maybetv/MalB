from flask import Flask, Response, request
import requests
import re

app = Flask(__name__)

PLAYLIST_URL = "https://premiumplugx.com/htt/hot.php?playlist=1"

@app.route('/stream.m3u8')
def proxy_stream():
    try:
        res = requests.get(PLAYLIST_URL)
        playlist_text = res.text
        
        target_url = None
        cookie_value = None
        
        lines = playlist_text.split('\n')
        for i, line in enumerate(lines):
            if 'Bigboss 24/7 live-MALAYALAM' in line:
                for j in range(i, min(i + 15, len(lines))):
                    if '.m3u8' in lines[j] and 'http' in lines[j]:
                        target_url = lines[j].split('|')[0].strip()
                    if 'hdntl=' in lines[j]:
                        match = re.search(r'(hdntl=[^&\s"]+)', lines[j])
                        if match:
                            cookie_value = match.group(1)
                break
        
        if not target_url or not cookie_value:
            return "Stream not found", 404

        headers = {
            'User-Agent': 'Hotstar;in.startv.hotstar/25.02.24.8.11169@Premium Plugx(Android/15)',
            'Referer': 'https://www.hotstar.com/',
            'Origin': 'https://www.hotstar.com',
            'Cookie': cookie_value
        }
        
        # ഹോട്ട്സ്റ്റാർ സ്ട്രീം ഡാറ്റ നേരിട്ട് വാങ്ങി പ്ലെയറിലേക്ക് പാസ് ചെയ്യുന്നു
        resp = requests.get(target_url, headers=headers, stream=True)
        
        return Response(
            resp.iter_content(chunk_size=1024),
            content_type=resp.headers.get('content-type', 'application/vnd.apple.mpegurl')
        )
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
