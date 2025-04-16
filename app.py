from flask import Flask, request, jsonify
from pytube import YouTube
import os
import tempfile
import requests

app = Flask(__name__)

API_KEY = os.getenv("APIVIDEO_API_KEY")

def download_youtube_video(url):
    yt = YouTube(url)
    stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    stream.download(output_path=os.path.dirname(temp_file.name), filename=os.path.basename(temp_file.name))
    return temp_file.name

def upload_and_trim(video_path, start, end, title):
    # Step 1: Upload video to api.video
    video_url = "https://api.api.video/v1/videos"
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    
    with open(video_path, "rb") as f:
        response = requests.post(video_url, headers=headers, files={"file": f})

    if response.status_code != 200:
        return {"error": "Failed to upload video to api.video"}

    video_id = response.json()["video"]["id"]

    # Step 2: Clip video using API
    clip_url = f"https://api.api.video/v1/videos/{video_id}/clips"
    clip_data = {
        "start": start,
        "end": end
    }

    clip_response = requests.post(clip_url, headers=headers, json=clip_data)

    if clip_response.status_code != 200:
        return {"error": "Failed to create video clip"}

    clip_data = clip_response.json()
    return {
        "original": response.json()["video"]["playbackUrl"],
        "trimmed": clip_data["clip"]["playbackUrl"]
    }

@app.route("/clip", methods=["POST"])
def clip_videos():
    try:
        data = request.get_json(force=True) # force=True ensures it parses JSON even if headers aren't set perfectly
        print(data)
        main_url = data["mainUrl"]
        background_url = data.get("backgroundUrl")
        start = int(data["startSeconds"])
        end = int(data["endSeconds"])
        result = {}

        main_path = download_youtube_video(main_url)
        result["main"] = upload_and_trim(main_path, start, end, "Main Video")
        os.remove(main_path)

        if background_url:
            bg_path = download_youtube_video(background_url)
            result["background"] = upload_and_trim(bg_path, start, end, "Background Video")
            os.remove(bg_path)

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
