// Local mock of the Worker for UI QA: runs the REAL src/index.js under Node, with the target network
// replaced by offline fixtures (dev/fixtures.mjs). No Cloudflare account, no login, no outbound requests.
// Usage: ALLOWED_ORIGINS=http://127.0.0.1:8766 PORT=8787 node dev/serve.mjs
import http from "node:http";
import worker from "../src/index.js";
import { makeFetch } from "./fixtures.mjs";

const PORT = +(process.env.PORT || 8787);
const env = { ALLOWED_ORIGINS: process.env.ALLOWED_ORIGINS || "http://127.0.0.1:8766", RL_IP_PER_10MIN: process.env.RL_IP_PER_10MIN || "500", RL_DOMAIN_PER_10MIN: process.env.RL_DOMAIN_PER_10MIN || "100", __fetchForTests: makeFetch() };
http.createServer(async (req, res) => {
  const chunks = [];
  for await (const c of req) chunks.push(c);
  const headers = new Headers();
  for (const [k, v] of Object.entries(req.headers)) if (typeof v === "string") headers.set(k, v);
  headers.set("CF-Connecting-IP", req.socket.remoteAddress || "127.0.0.1");
  const r = await worker.fetch(new Request("http://127.0.0.1:" + PORT + req.url, { method: req.method, headers, body: ["GET", "HEAD", "OPTIONS"].includes(req.method) ? undefined : Buffer.concat(chunks) }), env);
  res.writeHead(r.status, Object.fromEntries(r.headers));
  res.end(Buffer.from(await r.arrayBuffer()));
}).listen(PORT, "127.0.0.1", () => process.stdout.write("mock worker on http://127.0.0.1:" + PORT + "\n"));
