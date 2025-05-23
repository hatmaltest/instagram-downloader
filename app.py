from flask import Flask, request, jsonify, send_file
import subprocess
import os
import re
import tempfile

app = Flask(name)

@app.route('/')
def home():
    return "Instagram Downloader Backend is running!"

@app.route('/download', methods=['POST'])
def download_instagram_video():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    if not re.match(r'https?://(?:www\.)?instagram\.com/(p|reel|tv|stories)/[a-zA-Z0-9_-]+/?', url):
        return jsonify({"error": "Invalid Instagram URL format"}), 400

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_template = os.path.join(tmpdir, '%(id)s.%(ext)s')

            command = [
                "yt-dlp",
                "--restrict-filenames",
                "-o", output_template,
                "--max-downloads", "1",
                "--format", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
                url
            ]

            result = subprocess.run(command, capture_output=True, text=True, check=True)

            downloaded_file = None
            for filename in os.listdir(tmpdir):
                if filename.endswith(('.mp4', '.mkv', '.webm')):
                    downloaded_file = os.path.join(tmpdir, filename)
                    break

            if downloaded_file and os.path.exists(downloaded_file):
                return send_file(downloaded_file, mimetype='video/mp4')
            else:
                print("yt-dlp stdout:", result.stdout)
                print("yt-dlp stderr:", result.stderr)
                return jsonify({"error": "Video file not found after download. yt-dlp output in logs."}), 500

    except subprocess.CalledProcessError as e:
        print("yt-dlp error output:", e.stderr)
        return jsonify({"error": f"Failed to download video: {e.stderr}"}), 500
    except Exception as e:
        print("General error:", str(e))
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if name == 'main':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))
