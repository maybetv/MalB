from flask import Flask, Response, request
import requests

app = Flask(__name__)

PLAYLIST_URL = "https://premiumplugx.com/htt/hot.php?playlist=1"

@app.route('/playlist.m3u')
def get_playlist():
    try:
        # സോഴ്സ് പ്ലേലിസ്റ്റ് ഫെച്ച് ചെയ്യുന്നു
        res = requests.get(PLAYLIST_URL)
        playlist_text = res.text
        
        # ബിഗ് ബോസ് മലയാളം സെക്ഷൻ മാത്രം കണ്ടെത്തി എക്സ്ട്രാക്ട് ചെയ്യുന്നു
        lines = playlist_text.split('\n')
        extracted_block = []
        capture = False
        
        for line in lines:
            if 'Bigboss 24/7 live-MALAYALAM' in line:
                capture = True
            if capture:
                extracted_block.append(line)
                # ലിങ്ക് അവസാനിക്കുന്ന ഭാഗം വരെ എടുക്കുന്നു
                if line.startswith('https://') and '|cookie=' in line:
                    break
        
        if not extracted_block:
            return "Stream pattern not found", 404
            
        # പ്രോപ്പർ M3U ഫോർമാറ്റ് തയ്യാറാക്കുന്നു
        final_m3u = "#EXTM3U\n" + "\n".join(extracted_block)
        
        return Response(final_m3u, content_type='audio/x-mpegurl')
        
    except Exception as e:
        return str(e), 500

@app.route('/')
def home():
    return "M3U Generator is Live!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
