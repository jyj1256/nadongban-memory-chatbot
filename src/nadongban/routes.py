from flask import Blueprint, current_app, jsonify, render_template, request


web = Blueprint("web", __name__)


@web.get("/")
def index():
    return render_template("index.html")


@web.post("/api/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    try:
        result = current_app.extensions["chatbot"].chat(payload.get("message", ""))
        return jsonify(result)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except Exception:
        current_app.logger.exception("Chat request failed")
        return jsonify({"error": "답변 생성 중 오류가 발생했습니다."}), 500


@web.get("/api/health")
def health():
    store = current_app.extensions["memory_store"]
    return jsonify({"status": "ok", "memory_count": store.count()})


@web.delete("/api/memories")
def clear_memories():
    current_app.extensions["memory_store"].clear()
    return jsonify({"status": "cleared"})
