FROM node:22-alpine

WORKDIR /app

COPY frontend/package.json .
RUN npm install --omit=dev

COPY frontend/server.js .
COPY frontend/public ./public

EXPOSE 3000

CMD ["npm", "start"]
