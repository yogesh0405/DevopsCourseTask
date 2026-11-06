const express = require("express");
const path = require("node:path");

const app = express();
const port = process.env.PORT || 3000;
const host = process.env.HOST || "0.0.0.0";
const backendUrl = (process.env.BACKEND_URL || "http://localhost:5000").replace(/\/$/, "");

app.use(express.json());
app.use(express.static(path.join(__dirname, "public")));

app.use("/api", async (req, res) => {
  try {
    const options = { method: req.method };
    if (req.method !== "GET" && req.method !== "HEAD") {
      options.headers = { "Content-Type": "application/json" };
      options.body = JSON.stringify(req.body ?? {});
    }

    const response = await fetch(`${backendUrl}/api${req.url}`, options);
    const body = await response.text();
    res.status(response.status);

    const contentType = response.headers.get("content-type");
    if (contentType) res.set("Content-Type", contentType);
    res.send(body);
  } catch (error) {
    console.error("API proxy request failed:", error);
    res.status(502).json({ error: "The to-do API is unavailable. Please try again." });
  }
});

app.listen(port, host, () => {
  console.log(`Frontend running at http://localhost:${port}`);
});
