from flask import Flask, Response, request
import requests

app = Flask(__name__)

# നിങ്ങൾ തന്ന പുതിയ പ്ലേലിസ്റ്റ് ലിങ്ക്
PLAYLIST_URL = "https://premiumplugx.com/htt/hot.php?playlist=1"

@app.route('/stream.m3u8')
def proxy_stream():
    try:
        # പ്ലേലിസ്റ്റിൽ നിന്ന് ഡാറ്റ എടുക്കുന്നു (ഇവിടെ ബിഗ് ബോസ് പോലുള്ള ചാനൽ ലിങ്കുകൾ ഫെച്ച് ചെയ്യാം)
        res = requests.get(PLAYLIST_URL)
        playlist_data = res.text
        
        # ഉദാഹരണത്തിന് ആദ്യത്തെ .m3u8 ലിങ്കും അതിന്റെ കുക്കിയും ഇവിടെ എക്സ്ട്രാക്ട് ചെയ്യാം.
        # നിലവിൽ നമ്മൾ നേരിട്ട് ഹോട്ട്സ്റ്റാർ സ്ട്രീമിലേക്ക് പ്രോക്സി സെറ്റ് ചെയ്യുന്നു:
        target_url = "https://live09p.hotstar.com/mp2/incagbsgallow-biggboss-mal-2026/28fdd2300bf04a60ac3c3318ff009886/index_6.m3u8"
        cookie_value = "hdntl=exp=1793746809~acl=%2f*~id=d4d0bc38da0a57b34397e630515dd242~data=hdntl~hmac=87827c67ee5afb4712a5551f0537298f8f5a50e0bb20ea1f3dfe28c25cd1a3c5"
        
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
