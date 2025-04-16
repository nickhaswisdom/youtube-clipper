from flask import Flask, request, jsonify
from pytube import YouTube
import os
import tempfile
from apivideo import ApiVideoClient

app = Flask(__name__)

API_KEY = os.getenv("APIVIDEO_API_KEY")
client = ApiVideoClient(api_key=API_KEY)

def download_youtube_video(url):
    yt = YouTube(url)
    stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    stream.download(output_path=os.path.dirname(temp_file.name), filename=os.path.basename(temp_file.name))
    return temp_file.name

def upload_and_trim(video_path, start, end, title):
    video = client.videos.create(title=title)
    with open(video_path, "rb") as f:
        client.videos.upload(video.video_id, f)
    clip = client.video_clipping.create(video.video_id, start, end)
    return {
        "original": video.assets['player'],
        "trimmed": clip.assets['player']
    }

@app.route("/clip", methods=["POST"])
def clip_videos():
    try:
        data = request.get_json()
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
