from flask import Flask, Response, request
import requests
import re

app = Flask(__name__)

# നിങ്ങൾ തന്ന പ്ലേലിസ്റ്റ് സോഴ്സ് ലിങ്ക്
PLAYLIST_URL = "https://premiumplugx.com/htt/hot.php?playlist=1"

@app.route('/stream.m3u8')
def proxy_stream():
    try:
        # പ്ലേലിസ്റ്റ് ഡാറ്റ ഡൗൺലോഡ് ചെയ്യുന്നു
        res = requests.get(PLAYLIST_URL)
        playlist_text = res.text
        
        # ബിഗ് ബോസ് മലയാളം (Bigboss 24/7 live-MALAYALAM) എന്ന ഭാഗം സെർച്ച് ചെയ്ത് ലിങ്ക് എടുക്കുന്നു
        # സ്ക്രീൻഷോട്ടിൽ കണ്ടതുപോലെ മലയാലം ലിങ്കും കുക്കിയും കണ്ടെത്തുന്നു
        target_url = None
        cookie_value = None
        
        lines = playlist_text.split('\n')
        for i, line in enumerate(lines):
            if 'Bigboss 24/7 live-MALAYALAM' in line:
                # തൊട്ടടുത്ത വരികളിൽ കിടക്കുന്ന .m3u8 ലിങ്കും കുക്കിയും കണ്ടെത്തുക
                for j in range(i, min(i + 15, len(lines))):
                    if '.m3u8' in lines[j] and 'http' in lines[j]:
                        target_url = lines[j].split('|')[0].strip()
                    if 'hdntl=' in lines[j]:
                        # കുക്കി വാല്യൂ എക്സ്ട്രാക്ട് ചെയ്യുന്നു
                        match = re.search(r'(hdntl=[^&\s"]+)', lines[j])
                        if match:
                            cookie_value = match.group(1)
                break
        
        # ഒരുവളവ് ഡിഫോൾട്ട് ലിങ്ക് കിട്ടിയില്ലെങ്കിൽ ബാക്ക്അപ്പ്
        if not target_url:
            target_url = "https://live09p.hotstar.com/mp2/incagbsgallow-biggboss-mal-2026/28fdd2300bf04a60ac3c3318ff009886/index_6.m3u8"
        if not cookie_value:
            cookie_value = "hdntl=exp=1793908046~acl=%2f*~id=5da1ebd91eed6e7e9efbbd5ed35d7506~data=hdntl~hmac=9ed9adb9d5e065f4bdcb1b36ae25cfb2a3663a6cd0fdf5e0c29719ce0935a"

        headers = {
            'User-Agent': 'Hotstar;in.startv.hotstar/25.02.24.8.11169@Premium Plugx(Android/15)',
            'Referer': 'https://www.hotstar.com/',
            'Origin': 'https://www.hotstar.com',
            'Cookie': cookie_value
        }
        
        resp = requests.get(target_url, headers=headers, stream=True)
        
        return Response(
            resp.iter_content(chunk_size=1024),
            content_type=resp.headers.get('content-type')
        )
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
