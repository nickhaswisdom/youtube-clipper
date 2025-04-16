from flask import Flask, request, jsonify
import traceback

app = Flask(__name__)

@app.route("/clip", methods=["POST"])
def clip_videos():
    try:
        data = request.get_json(force=True)
        print("Data received:", data)

        main_url = data.get("mainUrl")
        background_url = data.get("backgroundUrl")
        start = int(data.get("startSeconds", 0))
        end = int(data.get("endSeconds", 0))

        if not main_url or not background_url:
            return jsonify({"status": "error", "message": "Missing YouTube URLs"}), 400

        print("Main URL:", main_url)
        print("Background URL:", background_url)
        print("Start:", start)
        print("End:", end)

        # 👇 Simulated success (no actual YouTube or video processing logic here)
        return jsonify({
            "status": "success",
            "message": "Simulated video processing complete.",
            "clipUrls": {
                "mainClip": "https://example.com/output-main.mp4",
                "backgroundClip": "https://example.com/output-bg.mp4"
            }
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
