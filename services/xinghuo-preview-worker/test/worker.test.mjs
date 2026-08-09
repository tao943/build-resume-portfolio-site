import test from "node:test";
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";


const workerUrl = new URL("../src/worker.mjs", import.meta.url);
const fixtureUrl = new URL(
  "../../../competition/xinghuo-cup-mvp/contracts/preview-request.example.json",
  import.meta.url,
);

async function loadWorker() {
  assert.equal(existsSync(workerUrl), true, "preview worker is missing");
  return (await import(workerUrl.href)).default;
}

function validRequest() {
  return JSON.parse(readFileSync(fixtureUrl, "utf8"));
}

class MemoryKV {
  constructor() {
    this.data = new Map();
  }

  async put(key, value) {
    this.data.set(key, value);
  }

  async get(key, type) {
    const value = this.data.get(key) ?? null;
    return type === "json" && value ? JSON.parse(value) : value;
  }
}

function environment() {
  return {
    PREVIEWS: new MemoryKV(),
    PREVIEW_WRITE_TOKEN: "test-secret",
  };
}

test("create requires bearer authentication", async () => {
  const worker = await loadWorker();
  const response = await worker.fetch(
    new Request("https://preview.test/api/v1/competition/previews", {
      method: "POST",
    }),
    environment(),
  );
  assert.equal(response.status, 401);
});

test("invalid preview input returns validation details", async () => {
  const worker = await loadWorker();
  const response = await worker.fetch(
    new Request("https://preview.test/api/v1/competition/previews", {
      method: "POST",
      headers: {
        authorization: "Bearer test-secret",
        "content-type": "application/json",
      },
      body: JSON.stringify({ generated_html: "<script>alert(1)</script>" }),
    }),
    environment(),
  );
  assert.equal(response.status, 422);
  const result = await response.json();
  assert.equal(result.error, "validation_failed");
  assert.ok(result.details.length > 0);
});

test("malformed JSON returns 400 without throwing", async () => {
  const worker = await loadWorker();
  const response = await worker.fetch(
    new Request("https://preview.test/api/v1/competition/previews", {
      method: "POST",
      headers: { authorization: "Bearer test-secret" },
      body: "{",
    }),
    environment(),
  );
  assert.equal(response.status, 400);
  assert.equal((await response.json()).error, "invalid_json");
});

test("oversized payloads are rejected before parsing", async () => {
  const worker = await loadWorker();
  const response = await worker.fetch(
    new Request("https://preview.test/api/v1/competition/previews", {
      method: "POST",
      headers: {
        authorization: "Bearer test-secret",
        "content-length": "512001",
      },
      body: "{}",
    }),
    environment(),
  );
  assert.equal(response.status, 413);
});

test("missing KV binding returns a service error", async () => {
  const worker = await loadWorker();
  const response = await worker.fetch(
    new Request("https://preview.test/api/v1/competition/previews", {
      method: "POST",
      headers: { authorization: "Bearer test-secret" },
      body: JSON.stringify(validRequest()),
    }),
    { PREVIEW_WRITE_TOKEN: "test-secret" },
  );
  assert.equal(response.status, 503);
  assert.equal((await response.json()).error, "storage_unavailable");
});

test("creates and serves a CSP-protected immutable preview", async () => {
  const worker = await loadWorker();
  const env = environment();
  const payload = validRequest();
  const create = await worker.fetch(
    new Request("https://preview.test/api/v1/competition/previews", {
      method: "POST",
      headers: {
        authorization: "Bearer test-secret",
        "content-type": "application/json",
      },
      body: JSON.stringify(payload),
    }),
    env,
  );
  assert.equal(create.status, 201);
  const result = await create.json();
  assert.match(result.preview_id, /^preview_[a-f0-9]{32}$/);
  assert.match(result.preview_url, /^https:\/\/preview\.test\/p\/[a-f0-9]{32}$/);
  assert.deepEqual(result.checks, {
    security: "passed",
    content_fidelity: "passed",
    responsive: "passed",
    template_independence: "passed",
  });

  const publicResponse = await worker.fetch(new Request(result.preview_url), env);
  assert.equal(publicResponse.status, 200);
  assert.equal(await publicResponse.text(), payload.generated_html);
  assert.match(
    publicResponse.headers.get("content-security-policy"),
    /default-src 'none'/,
  );
  assert.equal(publicResponse.headers.get("x-content-type-options"), "nosniff");
  assert.equal(publicResponse.headers.get("cache-control"), "public, max-age=31536000, immutable");

  const status = await worker.fetch(
    new Request(`https://preview.test/api/v1/competition/previews/${result.preview_id}`, {
      headers: { authorization: "Bearer test-secret" },
    }),
    env,
  );
  assert.equal(status.status, 200);
  const statusBody = await status.json();
  assert.equal(statusBody.preview_id, result.preview_id);
  assert.equal("payload" in statusBody, false);
});

test("status lookup requires authentication", async () => {
  const worker = await loadWorker();
  const response = await worker.fetch(
    new Request(`https://preview.test/api/v1/competition/previews/preview_${"a".repeat(32)}`),
    environment(),
  );
  assert.equal(response.status, 401);
});

test("unknown public preview returns 404", async () => {
  const worker = await loadWorker();
  const response = await worker.fetch(
    new Request(`https://preview.test/p/${"a".repeat(32)}`),
    environment(),
  );
  assert.equal(response.status, 404);
});
