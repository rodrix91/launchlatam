// Consent-authorization regressions: only explicit own request fields count.
// All outgoing scanner traffic is fixture-driven. No external network calls.
import test from "node:test";
import assert from "node:assert/strict";
import worker from "../src/index.js";
import { makeFetch } from "../dev/fixtures.mjs";

const ORIGIN = "https://rodrix91.github.io";
const TARGET = "https://www.fixture-clean.com.ar/";
let sequence = 0;

async function requestScan(body, { contentType = "application/json", query = "", method = "POST" } = {}) {
  const log = [];
  const url = "https://worker.example.test/scan" + query;
  const request = new Request(url, {
    method,
    headers: {
      Origin: ORIGIN,
      "Content-Type": contentType,
      "CF-Connecting-IP": "203.0.113." + (++sequence),
    },
    ...(method === "POST" ? { body } : {}),
  });
  const res = await worker.fetch(request, {
    ALLOWED_ORIGINS: ORIGIN,
    __fetchForTests: makeFetch(log),
  });
  return { status: res.status, data: await res.json(), log };
}

test("inherited consent and URL cannot trigger a scan", async () => {
  const body = '{"__proto__":{"consent":"1","url":"' + TARGET + '"}}';
  const result = await requestScan(body);
  assert.equal(result.status, 400);
  assert.equal(result.data.error, "consent_required");
  assert.equal(result.log.length, 0);
});

test("own URL without own consent cannot inherit authorization", async () => {
  const body = '{"url":"' + TARGET + '","__proto__":{"consent":"1"}}';
  const result = await requestScan(body);
  assert.equal(result.status, 400);
  assert.equal(result.data.error, "consent_required");
  assert.equal(result.log.length, 0);
});

test("own consent cannot inherit a target URL from a crafted prototype", async () => {
  const body = '{"consent":"1","__proto__":{"url":"' + TARGET + '"}}';
  const result = await requestScan(body);
  assert.equal(result.status, 400);
  assert.equal(result.data.ok, false);
  assert.equal(result.log.length, 0);
});

test("non-scalar JSON consent cannot authorize a scan or crash the worker", async () => {
  for (const consent of [[1], { toString: null }, null, true]) {
    const result = await requestScan(JSON.stringify({ url: TARGET, consent }));
    assert.equal(result.status, 400);
    assert.equal(result.data.error, "consent_required");
    assert.equal(result.log.length, 0);
  }
});

test("invalid JSON top-level arrays and primitive payloads fail closed", async () => {
  for (const body of ['[{"url":"' + TARGET + '","consent":"1"}]', '"1"', "null", "1"]) {
    const result = await requestScan(body);
    assert.equal(result.status, 400);
    assert.equal(result.data.error, "invalid_url");
    assert.equal(result.log.length, 0);
  }
});

test("own JSON fields still work even if an irrelevant prototype key is present", async () => {
  const body = '{"__proto__":{"consent":"0","url":"https://invalid.example.test/"},"consent":"1","url":"' + TARGET + '"}';
  const result = await requestScan(body);
  assert.equal(result.status, 200, JSON.stringify(result.data));
  assert.equal(result.data.ok, true);
  assert.equal(result.data.target.host, "www.fixture-clean.com.ar");
  assert.ok(result.log.length > 0);
});

test("legitimate URL-encoded form POST preserves explicit consent", async () => {
  const body = new URLSearchParams({ url: TARGET, consent: "1" }).toString();
  const result = await requestScan(body, { contentType: "application/x-www-form-urlencoded" });
  assert.equal(result.status, 200, JSON.stringify(result.data));
  assert.equal(result.data.ok, true);
});

test("GET remains compatible with explicit query-string consent and target", async () => {
  const query = "?" + new URLSearchParams({ url: TARGET, consent: "1" });
  const result = await requestScan(undefined, { method: "GET", query });
  assert.equal(result.status, 200, JSON.stringify(result.data));
  assert.equal(result.data.ok, true);
});
