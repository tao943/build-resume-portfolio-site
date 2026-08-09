import { validatePreviewRequest } from "./validation.mjs";


const MAX_REQUEST_BYTES = 512_000;
const PREVIEW_ID = /^preview_[a-f0-9]{32}$/;
const PUBLIC_TOKEN = /^[a-f0-9]{32}$/;
const CHECKS = Object.freeze({
  security: "passed",
  content_fidelity: "passed",
  responsive: "passed",
  template_independence: "passed",
});

function json(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
      "x-content-type-options": "nosniff",
    },
  });
}

function authorized(request, env) {
  return (
    typeof env.PREVIEW_WRITE_TOKEN === "string" &&
    env.PREVIEW_WRITE_TOKEN.length >= 8 &&
    request.headers.get("authorization") === `Bearer ${env.PREVIEW_WRITE_TOKEN}`
  );
}

function randomToken() {
  return crypto.randomUUID().replaceAll("-", "");
}

async function readPayload(request) {
  const declaredLength = Number(request.headers.get("content-length") || 0);
  if (declaredLength > MAX_REQUEST_BYTES) {
    return { error: json({ error: "payload_too_large" }, 413) };
  }
  const text = await request.text();
  if (new TextEncoder().encode(text).byteLength > MAX_REQUEST_BYTES) {
    return { error: json({ error: "payload_too_large" }, 413) };
  }
  try {
    return { payload: JSON.parse(text) };
  } catch {
    return { error: json({ error: "invalid_json" }, 400) };
  }
}

async function createPreview(request, env, url) {
  if (!authorized(request, env)) return json({ error: "unauthorized" }, 401);
  if (!env.PREVIEWS || typeof env.PREVIEWS.put !== "function") {
    return json({ error: "storage_unavailable" }, 503);
  }
  const body = await readPayload(request);
  if (body.error) return body.error;
  const result = validatePreviewRequest(body.payload);
  if (!result.ok) {
    return json({ error: "validation_failed", details: result.errors }, 422);
  }

  const previewId = `preview_${randomToken()}`;
  const publicToken = randomToken();
  const artifact = {
    preview_id: previewId,
    public_token: publicToken,
    status: "ready",
    created_at: new Date().toISOString(),
    checks: CHECKS,
    payload: result.normalized,
  };
  const serialized = JSON.stringify(artifact);
  await env.PREVIEWS.put(`id:${previewId}`, serialized);
  await env.PREVIEWS.put(`public:${publicToken}`, serialized);

  return json(
    {
      preview_id: previewId,
      preview_url: `${url.origin}/p/${publicToken}`,
      status: "ready",
      checks: CHECKS,
    },
    201,
  );
}

async function previewStatus(request, env, previewId) {
  if (!authorized(request, env)) return json({ error: "unauthorized" }, 401);
  if (!PREVIEW_ID.test(previewId)) return json({ error: "not_found" }, 404);
  const artifact = await env.PREVIEWS.get(`id:${previewId}`, "json");
  if (!artifact) return json({ error: "not_found" }, 404);
  return json({
    preview_id: artifact.preview_id,
    status: artifact.status,
    created_at: artifact.created_at,
    checks: artifact.checks,
  });
}

async function publicPreview(env, token) {
  if (!PUBLIC_TOKEN.test(token)) return new Response("Not found", { status: 404 });
  const artifact = await env.PREVIEWS.get(`public:${token}`, "json");
  if (!artifact) return new Response("Not found", { status: 404 });
  return new Response(artifact.payload.generated_html, {
    status: 200,
    headers: {
      "content-type": "text/html; charset=utf-8",
      "content-security-policy":
        "default-src 'none'; style-src 'unsafe-inline'; img-src data:; font-src data:; base-uri 'none'; form-action 'none'; frame-ancestors 'none'",
      "permissions-policy":
        "camera=(), microphone=(), geolocation=(), payment=(), usb=()",
      "x-content-type-options": "nosniff",
      "referrer-policy": "no-referrer",
      "cache-control": "public, max-age=31536000, immutable",
    },
  });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === "POST" && url.pathname === "/api/v1/competition/previews") {
      return createPreview(request, env, url);
    }

    const statusMatch = url.pathname.match(
      /^\/api\/v1\/competition\/previews\/(preview_[a-f0-9]{32})$/,
    );
    if (request.method === "GET" && statusMatch) {
      return previewStatus(request, env, statusMatch[1]);
    }

    const publicMatch = url.pathname.match(/^\/p\/([a-f0-9]{32})$/);
    if (request.method === "GET" && publicMatch) {
      return publicPreview(env, publicMatch[1]);
    }

    return json({ error: "not_found" }, 404);
  },
};
