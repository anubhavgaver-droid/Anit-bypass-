import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# क्लाउडफ्लेयर की टेस्ट कीज़ (बाद में अपनी कीज़ लगा सकते हैं)
TURNSTILE_SITE_KEY = os.environ.get("TURNSTILE_SITE_KEY", "0x4AAAAAAEW2Ci6bkvsSt9JE")
TURNSTILE_SECRET_KEY = os.environ.get("TURNSTILE_SECRET_KEY", "0x4AAAAAAEW2CrKKwntMxBfDSRfXUr48arA")

@app.route('/')
def home():
    token = request.args.get('v') or request.args.get('token') or ""
    # जहाँ यूज़र को भेजना है (शॉर्टनर लिंक या टेलीग्राम बॉट)
    dest = request.args.get('dest', 'https://get2short.com')
    
    return render_template('verify.html', site_key=TURNSTILE_SITE_KEY, token=token, dest=dest)

@app.route('/api/verify', methods=['POST'])
def verify_captcha():
    data = request.json or {}
    token = data.get('cf_token')
    dest_url = data.get('dest')

    if not token:
        return jsonify({"success": False, "message": "Captcha required"}), 400

    # Cloudflare Server Validation
    verify_res = requests.post(
        "https://challenges.cloudflare.com/turnstile/v0/siteverify",
        data={
            "secret": TURNSTILE_SECRET_KEY,
            "response": token,
            "remoteip": request.remote_addr
        }
    ).json()

    if verify_res.get("success"):
        return jsonify({"success": True, "redirect_url": dest_url})
    else:
        return jsonify({"success": False, "message": "Verification failed"}), 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
