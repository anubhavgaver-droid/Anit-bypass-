import os
import base64
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# क्लाउडफ्लेयर की टेस्ट कीज़ (ज़रूरत पड़ने पर अपनी कीज़ बदलें)
TURNSTILE_SITE_KEY = os.environ.get("TURNSTILE_SITE_KEY", "0x4AAAAAAEW2Ci6bkvsSt9JE")
TURNSTILE_SECRET_KEY = os.environ.get("TURNSTILE_SECRET_KEY", "0x4AAAAAAEW2CrKKwntMxBfDSRfXUr48arA")

@app.route('/')
def home():
    # start.py से आने वाला encoded data या direct dest URL
    encoded_data = request.args.get('data', '')
    dest = request.args.get('dest', '')

    # Base64 Data Decoding (Anti-Bypass Gateway Logic)
    if encoded_data:
        try:
            dest = base64.b64decode(encoded_data).decode('utf-8')
        except Exception:
            dest = "https://t.me/SmartfilestorebyAcbot"

    # Fallback default destination
    if not dest:
        dest = "https://t.me/SmartfilestorebyAcbot"

    token = request.args.get('v') or request.args.get('token') or ""
    
    return render_template('verify.html', site_key=TURNSTILE_SITE_KEY, token=token, dest=dest)

@app.route('/api/verify', methods=['POST'])
def verify_captcha():
    data = request.json or {}
    token = data.get('cf_token')
    dest_url = data.get('dest')

    if not token:
        return jsonify({"success": False, "message": "Captcha required"}), 400

    # Cloudflare Server Validation
    try:
        verify_res = requests.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data={
                "secret": TURNSTILE_SECRET_KEY,
                "response": token,
                "remoteip": request.remote_addr
            },
            timeout=10
        ).json()
    except Exception as e:
        return jsonify({"success": False, "message": f"Validation Error: {str(e)}"}), 500

    if verify_res.get("success"):
        return jsonify({"success": True, "redirect_url": dest_url})
    else:
        return jsonify({"success": False, "message": "Verification failed"}), 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
