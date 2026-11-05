import json
from itertools import count
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

API_RESPONSE_FILE = Path(__file__).with_name("api.json")

todos = []
next_id = count(1)


@app.get("/api")
def api_status():
    with API_RESPONSE_FILE.open(encoding="utf-8") as response_file:
        return jsonify(json.load(response_file))


@app.get("/api/todos")
def list_todos():
    return jsonify(todos)


@app.post("/api/todos")
def create_todo():
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "A task title is required."}), 400

    todo = {"id": next(next_id), "title": title.strip(), "completed": False}
    todos.append(todo)
    return jsonify(todo), 201


@app.patch("/api/todos/<int:todo_id>")
def toggle_todo(todo_id):
    todo = next((item for item in todos if item["id"] == todo_id), None)
    if todo is None:
        return jsonify({"error": "Task not found."}), 404

    todo["completed"] = not todo["completed"]
    return jsonify(todo)


@app.delete("/api/todos/<int:todo_id>")
def delete_todo(todo_id):
    todo = next((item for item in todos if item["id"] == todo_id), None)
    if todo is None:
        return jsonify({"error": "Task not found."}), 404

    todos.remove(todo)
    return "", 204


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
