from flask import Flask, Response, request
import requests
import re

app = Flask(__name__)

PLAYLIST_URL = "https://premiumplugx.com/htt/hot.php?playlist=1"

@app.route('/playlist.m3u')
def get_playlist():
    try:
        # സോഴ്സ് പ്ലേലിസ്റ്റ് ഫെച്ച് ചെയ്യുന്നു
        res = requests.get(PLAYLIST_URL)
        playlist_text = res.text
        
        target_url = None
        cookie_value = None
        logo_url = ""
        
        lines = playlist_text.split('\n')
        for i, line in enumerate(lines):
            if 'Bigboss 24/7 live-MALAYALAM' in line:
                # ലോഗോ എടുക്കുന്നു
                if 'tvg-logo="' in line:
                    logo_match = re.search(r'tvg-logo="([^"]+)"', line)
                    if logo_match:
                        logo_url = logo_match.group(1)
                
                # ലിങ്കും കുക്കിയും കണ്ടെത്തുന്നു
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

        # IPTV പ്ലെയറുകൾക്ക് (TiviMate, VLC) കറക്റ്റ് ആയി സപ്പോർട്ട് ചെയ്യുന്ന M3U ഫോർമാറ്റ്
        m3u_content = f"""#EXTM3U
#EXTINF:-1 tvg-name="Bigboss 24/7 live-MALAYALAM" tvg-logo="{logo_url}" group-title="Entertainment",Bigboss 24/7 live-MALAYALAM
#EXTVLCOPT:http-user-agent=Hotstar;in.startv.hotstar/25.02.24.8.11169@Premium Plugx(Android/15)
#EXTVLCOPT:http-referrer=https://www.hotstar.com/
#EXTVLCOPT:http-extra-headers=Origin: https://www.hotstar.com
#EXTVLCOPT:http-cookie={cookie_value}
{target_url}|cookie={cookie_value}&referer=https://www.hotstar.com/&origin=https://www.hotstar.com&user-agent=Hotstar;in.startv.hotstar/25.02.24.8.11169@Premium Plugx(Android/15)
"""
        
        return Response(m3u_content, content_type='audio/x-mpegurl')
        
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
