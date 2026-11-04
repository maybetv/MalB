from flask import Flask, Response, request
import requests
import re
import time
import threading

app = Flask(__name__)

PLAYLIST_URL = "https://premiumplugx.com/htt/hot.php?playlist=1"

# ഗ്ലോബൽ വേരിയബിളുകൾ (ഡാറ്റ സ്റ്റോർ ചെയ്യാൻ)
cached_m3u = ""
last_updated = 0

def update_playlist_cache():
    global cached_m3u, last_updated
    while True:
        try:
            print("Fetching fresh playlist from source...")
            res = requests.get(PLAYLIST_URL)
            playlist_text = res.text
            
            target_url = None
            cookie_value = None
            logo_url = ""
            
            lines = playlist_text.split('\n')
            for i, line in enumerate(lines):
                if 'Bigboss 24/7 live-MALAYALAM' in line:
                    if 'tvg-logo="' in line:
                        logo_match = re.search(r'tvg-logo="([^"]+)"', line)
                        if logo_match:
                            logo_url = logo_match.group(1)
                    
                    for j in range(i, min(i + 15, len(lines))):
                        if '.m3u8' in lines[j] and 'http' in lines[j]:
                            target_url = lines[j].split('|')[0].strip()
                        if 'hdntl=' in lines[j]:
                            match = re.search(r'(hdntl=[^&\s"]+)', lines[j])
                            if match:
                                cookie_value = match.group(1)
                    break
            
            if target_url and cookie_value:
                # ഫ്രഷ് ആയ M3U ഫോർമാറ്റ് ജനറേറ്റ് ചെയ്യുന്നു
                cached_m3u = f"""#EXTM3U
#EXTINF:-1 tvg-name="Bigboss 24/7 live-MALAYALAM" tvg-logo="{logo_url}" group-title="Entertainment",Bigboss 24/7 live-MALAYALAM
#EXTVLCOPT:http-user-agent=Hotstar;in.startv.hotstar/25.02.24.8.11169@Premium Plugx(Android/15)
#EXTVLCOPT:http-referrer=https://www.hotstar.com/
#EXTVLCOPT:http-extra-headers=Origin: https://www.hotstar.com
#EXTVLCOpt:http-cookie={cookie_value}
{target_url}|cookie={cookie_value}&referer=https://www.hotstar.com/&origin=https://www.hotstar.com&user-agent=Hotstar;in.startv.hotstar/25.02.24.8.11169@Premium Plugx(Android/15)
"""
                last_updated = time.time()
                print("Playlist cache updated successfully!")
        except Exception as e:
            print(f"Error updating cache: {e}")
            
        # ഓരോ 3 മണിക്കൂർ കൂടുമ്പോൾ (10800 സെക്കൻഡ്) ഇത് ഓട്ടോമാറ്റിക്കായി അപ്ഡേറ്റ് ചെയ്യും
        time.sleep(10800)

# ബാക്ക്ഗ്രൗണ്ടിൽ റൺ ചെയ്യാൻ ഒരു ചെറിയ ത്രെഡ് സ്റ്റാർട്ട് ചെയ്യുന്നു
threading.Thread(target=update_playlist_cache, daemon=True).start()

@app.route('/playlist.m3u')
def get_playlist():
    global cached_m3u
    if cached_m3u:
        return Response(cached_m3u, content_type='audio/x-mpegurl')
    else:
        return "Initializing playlist, please wait...", 503

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
