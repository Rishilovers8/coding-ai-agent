"""Flask routes for Ramify RR web application."""

import os
import logging
import traceback

from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    send_file,
    flash,
    redirect,
    url_for,
)
from werkzeug.utils import secure_filename

from app.config import Config
from app.pipeline import run_pipeline, LANGUAGE_MAP

logger = logging.getLogger(__name__)


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )
    app.config.from_object(Config)

    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(Config.OUTPUT_FOLDER, exist_ok=True)

    def allowed_file(filename: str) -> bool:
        return "." in filename and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS

    @app.route("/")
    def index():
        return render_template(
            "index.html",
            languages=LANGUAGE_MAP,
            elevenlabs_configured=bool(Config.ELEVENLABS_API_KEY),
        )

    @app.route("/translate", methods=["POST"])
    def translate_video():
        if "video" not in request.files:
            return jsonify({"error": "No video file uploaded."}), 400

        file = request.files["video"]
        if file.filename == "":
            return jsonify({"error": "No file selected."}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": f"Invalid file type. Allowed: {', '.join(Config.ALLOWED_EXTENSIONS)}"}), 400

        target_lang = request.form.get("target_lang", "en")
        use_elevenlabs = request.form.get("use_elevenlabs") == "true"
        voice_id = request.form.get("voice_id", "").strip() or None

        filename = secure_filename(file.filename)
        video_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(video_path)

        try:
            result = run_pipeline(
                video_path=video_path,
                target_lang=target_lang,
                use_elevenlabs=use_elevenlabs,
                voice_id=voice_id,
            )

            output_basename = os.path.basename(result["output_video"])

            return jsonify({
                "success": True,
                "download_url": url_for("download_file", filename=output_basename),
                "source_lang": result["source_lang_name"],
                "target_lang": result["target_lang_name"],
                "transcription": result["transcription"],
                "translation": result["translation"],
            })

        except Exception as e:
            logger.error("Pipeline error: %s", traceback.format_exc())
            return jsonify({"error": str(e)}), 500

        finally:
            try:
                os.remove(video_path)
            except OSError:
                pass

    @app.route("/download/<filename>")
    def download_file(filename):
        file_path = os.path.join(Config.OUTPUT_FOLDER, secure_filename(filename))
        if not os.path.exists(file_path):
            return jsonify({"error": "File not found."}), 404
        return send_file(file_path, as_attachment=True, download_name=f"ramify_translated_{filename}")

    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "app": "Ramify RR"})

    return app
