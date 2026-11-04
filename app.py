from flask import Flask, redirect, request
import requests
import re

app = Flask(__name__)

PLAYLIST_URL = "https://premiumplugx.com/htt/hot.php?playlist=1"

@app.route('/stream.m3u8')
def proxy_stream():
    try:
        # പ്ലേലിസ്റ്റ് ഡാറ്റ ഫെച്ച് ചെയ്യുന്നു
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
            return "Stream not found in playlist", 404

        # പ്ലെയർ സപ്പോർട്ട് ചെയ്യുന്ന രീതിയിൽ ഒറിജിനൽ കുക്കിയും പൈപ്പും ചേർത്ത് ലിങ്ക് തയ്യാറാക്കുന്നു
        final_redirect_url = f"{target_url}|cookie={cookie_value}&referer=https://www.hotstar.com/&origin=https://www.hotstar.com"
        
        # പ്രോ ഡെവലപ്പർ വേ: ഡയറക്ട് റീഡയറക്ട് (HTTP 302) വഴി പ്ലെയറിനെ ഹോട്ട്സ്റ്റാറിലേക്ക് കണക്റ്റ് ചെയ്യുന്നു
        return redirect(final_redirect_url, code=302)
        
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
