from __future__ import annotations

import os
from pathlib import Path

from bson import ObjectId
from dotenv import load_dotenv
from flask import Flask, current_app, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient, ReturnDocument
from pymongo.collection import Collection
from pymongo.errors import PyMongoError
from pymongo.server_api import ServerApi

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

app = Flask(__name__)
CORS(app, resources={r"/api(?:/.*)?": {"origins": "http://localhost:3000"}})

mongo_client: MongoClient | None = None


class DatabaseConfigurationError(Exception):
    pass


def get_todos_collection() -> Collection:
    global mongo_client
    uri = os.environ.get("MONGODB_URI")
    if not uri:
        raise DatabaseConfigurationError("MONGODB_URI is not configured.")

    if mongo_client is None:
        mongo_client = MongoClient(
            uri,
            server_api=ServerApi("1"),
            serverSelectionTimeoutMS=5000,
        )

    database_name = os.environ.get("MONGODB_DATABASE", "todo_app")
    return mongo_client[database_name]["todos"]


def serialize_todo(todo: dict) -> dict:
    return {
        "id": str(todo["_id"]),
        "title": todo["title"],
        "description": todo["description"],
        "completed": todo["completed"],
    }


@app.errorhandler(DatabaseConfigurationError)
@app.errorhandler(PyMongoError)
def handle_database_error(error):
    current_app.logger.error("MongoDB request failed: %s", error)
    return jsonify({
        "error": "MongoDB is unavailable. Check MONGODB_URI and Atlas network access."
    }), 503


@app.get("/api")
@app.get("/api/todos")
def list_todos():
    todos = get_todos_collection().find().sort("_id", 1)
    return jsonify([serialize_todo(todo) for todo in todos])


@app.post("/api/todos")
def create_todo():
    data = request.get_json(silent=True) or {}
    title = data.get("itemName", data.get("title"))
    description = data.get("itemDescription", data.get("description"))
    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "An item name is required."}), 400
    if not isinstance(description, str) or not description.strip():
        return jsonify({"error": "An item description is required."}), 400

    todo = {
        "title": title.strip(),
        "description": description.strip(),
        "completed": False,
    }
    result = get_todos_collection().insert_one(todo)
    todo["_id"] = result.inserted_id
    return jsonify(serialize_todo(todo)), 201


@app.patch("/api/todos/<todo_id>")
def toggle_todo(todo_id):
    if not ObjectId.is_valid(todo_id):
        return jsonify({"error": "Task not found."}), 404

    collection = get_todos_collection()
    todo = collection.find_one({"_id": ObjectId(todo_id)})
    if todo is None:
        return jsonify({"error": "Task not found."}), 404

    updated = collection.find_one_and_update(
        {"_id": ObjectId(todo_id)},
        {"$set": {"completed": not todo["completed"]}},
        return_document=ReturnDocument.AFTER,
    )
    if updated is None:
        return jsonify({"error": "Task not found."}), 404
    return jsonify(serialize_todo(updated))


@app.delete("/api/todos/<todo_id>")
def delete_todo(todo_id):
    if not ObjectId.is_valid(todo_id):
        return jsonify({"error": "Task not found."}), 404

    result = get_todos_collection().delete_one({"_id": ObjectId(todo_id)})
    if result.deleted_count == 0:
        return jsonify({"error": "Task not found."}), 404

    return "", 204


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
