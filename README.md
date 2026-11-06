# To-Do App

The project is split into two small applications:

- `frontend/` — Express serves the browser interface.
- `backend/` — Flask provides the to-do JSON API.

Tasks are stored in MongoDB Atlas. `GET /api` and `GET /api/todos` return the
current to-do items.

## Set up MongoDB Atlas

1. Create a free MongoDB Atlas account and deploy a cluster.
2. In **Database Access**, create a database user and save its username and
   password. This is separate from your Atlas login.
3. In **Network Access**, add the public IP address of the machine running the
   backend. Avoid allowing access from all IP addresses except for temporary
   testing.
4. Choose **Connect** for your cluster, select **Drivers**, and copy the
   connection string. Replace its username, password, and cluster host with
   your values. URL-encode special characters in the database user's password.
5. From the project root, create a local environment file and edit it with the
   connection string:

   ```bash
   cp .env.example .env
   ```

   `.env` is ignored by Git; do not commit Atlas credentials.

For a local backend started outside Docker, export the settings before running
Flask:

```bash
export MONGODB_URI='mongodb+srv://...'
export MONGODB_DATABASE='todo_app'
```

The form submits item names and descriptions to Flask. Successful submissions
are saved in Atlas and redirect to a confirmation page; errors remain visible
on the form. The Flask API also lists these saved tasks at `/api`.
The Express frontend proxies `/api` requests to Flask, so browsers do not
connect directly to the backend.

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

Open <http://localhost:3000>. Stop the containers with `Ctrl+C`, or run
`docker compose down` in another terminal.

## Deploy on one EC2 instance without Docker

These deployment files target Ubuntu 24.04 with the default `ubuntu` user and
the repository at `/home/ubuntu/CI_Cd`. Nginx serves the public HTTP endpoint,
Express proxies `/api` requests to Flask, and Flask listens only on localhost.

1. Launch an Ubuntu EC2 instance. In its security group, allow SSH (port 22)
   only from your IP, and HTTP (port 80) from the clients that need access.
   Do not expose ports 3000 or 5000 publicly.
2. Connect over SSH and install the runtime packages:

   ```bash
   sudo apt update
   sudo apt install -y git python3 python3-venv python3-pip nodejs npm nginx
   node --version
   ```

   Use a Node.js release supported by the installed Express version (Node 18
   or newer).
3. Clone the repository and install dependencies:

   ```bash
   git clone <your-github-repository-url> /home/ubuntu/CI_Cd
   cd /home/ubuntu/CI_Cd
   python3 -m venv backend/.venv
   backend/.venv/bin/pip install -r backend/requirements.txt
   cd frontend
   npm ci --omit=dev
   cd ..
   ```

4. Create `/home/ubuntu/CI_Cd/.env` with `MONGODB_URI` and
   `MONGODB_DATABASE=todo_app`. Set the Atlas Network Access list to permit the
   instance's public egress IP. Keep the environment file private:

   ```bash
   chmod 600 .env
   ```

5. Install and start the systemd services and Nginx site:

   ```bash
   sudo cp deploy/todo-backend.service /etc/systemd/system/
   sudo cp deploy/todo-frontend.service /etc/systemd/system/
   sudo cp deploy/todo-app.nginx /etc/nginx/sites-available/todo-app
   sudo ln -sfn /etc/nginx/sites-available/todo-app /etc/nginx/sites-enabled/todo-app
   sudo rm -f /etc/nginx/sites-enabled/default
   sudo nginx -t
   sudo systemctl daemon-reload
   sudo systemctl enable --now todo-backend todo-frontend nginx
   ```

6. Open `http://<EC2-PUBLIC-IP>`. Check service status or logs with:

   ```bash
   sudo systemctl status todo-backend todo-frontend nginx
   sudo journalctl -u todo-backend -u todo-frontend -f
   ```

For production, configure HTTPS with a domain name and a TLS certificate
(for example, Certbot with Let's Encrypt). Keep SSH restricted to your IP and
do not expose the Flask port.

## Deploy locally with Minikube

The project has an Express frontend and a Flask backend. These commands build
both images inside Minikube, load the Atlas settings from the ignored `.env`
file into a Kubernetes Secret, and deploy both services:

```bash
minikube start

kubectl create secret generic todo-app-secrets \
  --from-env-file=.env \
  --dry-run=client -o yaml | kubectl apply -f -

minikube image build -t todo-backend:local -f backend/Dockerfile .
minikube image build -t todo-frontend:local -f frontend/Dockerfile .

kubectl apply -f k8s/todo-app.yaml
kubectl rollout status deployment/todo-backend
kubectl rollout status deployment/todo-frontend
```

Keep the frontend port-forward running:

```bash
kubectl port-forward service/todo-frontend 3000:3000
```

Open <http://localhost:3000>. Express forwards API calls to Flask inside the
cluster. If Atlas connections fail, ensure Atlas Network Access allows the
public egress IP used by the Minikube host.

To remove the Kubernetes deployment and local secret:

```bash
kubectl delete -f k8s/todo-app.yaml
kubectl delete secret todo-app-secrets
```
