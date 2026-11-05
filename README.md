# To-Do App

The project is split into two small applications:

- `frontend/` — Express serves the browser interface.
- `backend/` — Flask provides the to-do JSON API.

Tasks are stored in memory and reset when the Flask server restarts.

## Start the Flask backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

The API runs at <http://localhost:5000>.

## Start the Express frontend

In another terminal:

```bash
cd frontend
npm install
npm start
```

Open <http://localhost:3000>.

## Run with Docker

Build both images and start the app from the repository root:

```bash
docker compose up --build
```

Open <http://localhost:3000>. The Flask API is available at
<http://localhost:5000>. Stop the containers with `Ctrl+C`, or run
`docker compose down` in another terminal.
