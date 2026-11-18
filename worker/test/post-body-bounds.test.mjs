// Network-free regressions for bounded inbound Worker POST parsing.
import test from "node:test";
import assert from "node:assert/strict";
import worker from "../src/index.js";
import { makeFetch } from "../dev/fixtures.mjs";

const ORIGIN = "https://rodrix91.github.io";
const ENDPOINT = "https://w.example.workers.dev/scan";
const TARGET = "https://www.fixture-clean.com.ar/";
const ENCODER = new TextEncoder();
let serial = 0;

function env(log = []) {
  return { ALLOWED_ORIGINS: ORIGIN, __fetchForTests: makeFetch(log) };
}
function request(body, contentType = "application/x-www-form-urlencoded", headers = {}) {
  return new Request(ENDPOINT, {
    method: "POST",
    headers: {
      Origin: ORIGIN,
      "Content-Type": contentType,
      "CF-Connecting-IP": "198.51.100." + (++serial),
      ...headers,
    },
    body,
    ...(body instanceof ReadableStream ? { duplex: "half" } : {}),
  });
}
async function run(body, contentType, headers) {
  const calls = [];
  const response = await worker.fetch(request(body, contentType, headers), env(calls));
  return { status: response.status, body: await response.json(), calls };
}

test("POST body longer than 4096 bytes is rejected before scanning", async () => {
  const contents = new URLSearchParams({
    url: TARGET,
    consent: "1",
    padding: "X".repeat(4500),
  }).toString();
  const result = await run(contents);
  assert.equal(result.status, 413);
  assert.equal(result.body.error, "request_too_large");
  assert.equal(result.calls.length, 0, "oversized input must never fetch target");
  assert.equal(JSON.stringify(result.body).includes("XXXX"), false);
});

test("Content-Length above limit is rejected immediately", async () => {
  const result = await run(
    new URLSearchParams({ url: TARGET, consent: "1" }).toString(),
    "application/x-www-form-urlencoded",
    { "Content-Length": "4097" },
  );
  assert.equal(result.status, 413);
  assert.equal(result.body.error, "request_too_large");
  assert.equal(result.calls.length, 0);
});

test("stream with short first chunk and oversized second chunk is rejected", async () => {
  const stream = new ReadableStream({
    start(controller) {
      controller.enqueue(ENCODER.encode("url=" + encodeURIComponent(TARGET) + "&consent=1&padding="));
      controller.enqueue(ENCODER.encode("x".repeat(5000)));
      controller.close();
    },
  });
  const result = await run(stream);
  assert.equal(result.status, 413);
  assert.equal(result.body.error, "request_too_large");
  assert.equal(result.calls.length, 0);
});

test("counting UTF-8 bytes prevents multibyte character bypasses", async () => {
  const base = new URLSearchParams({ url: TARGET, consent: "1" }).toString();
  // Deliberately stream decoded non-ASCII text rather than percent-encoded form.
  const text = base + "&padding=" + "é".repeat(2048);
  assert.ok(text.length < 4096 && ENCODER.encode(text).byteLength > 4096);
  const result = await run(text);
  assert.equal(result.status, 413);
  assert.equal(result.body.error, "request_too_large");
  assert.equal(result.calls.length, 0);
});

test("exactly 4096 UTF-8 bytes still accepts a legitimate form", async () => {
  const prefix = new URLSearchParams({ url: TARGET, consent: "1" }).toString() + "&padding=";
  const text = prefix + "x".repeat(4096 - ENCODER.encode(prefix).byteLength);
  assert.equal(ENCODER.encode(text).byteLength, 4096);
  const result = await run(text);
  assert.equal(result.status, 200, JSON.stringify(result.body));
  assert.equal(result.body.ok, true);
  assert.ok(result.calls.length > 0, "accepted requests still scan using the fixture");
});

test("valid JSON POST retains original response and invalid JSON stays rejected", async () => {
  const valid = await run(JSON.stringify({ url: TARGET, consent: "1" }), "application/json");
  assert.equal(valid.status, 200, JSON.stringify(valid.body));
  assert.equal(valid.body.ok, true);
  const invalid = await run("{broken", "application/json");
  assert.equal(invalid.status, 400);
  assert.equal(invalid.body.error, "invalid_url");
  assert.equal(invalid.calls.length, 0);
});

test("oversized JSON also fails closed before parsing", async () => {
  const text = JSON.stringify({ url: TARGET, consent: "1", padding: "Z".repeat(5000) });
  const result = await run(text, "application/json");
  assert.equal(result.status, 413);
  assert.equal(result.body.error, "request_too_large");
  assert.equal(result.calls.length, 0);
});
