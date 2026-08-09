import test from "node:test";
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";


const validatorUrl = new URL("../src/validation.mjs", import.meta.url);

async function loadValidator() {
  assert.equal(existsSync(validatorUrl), true, "preview validator is missing");
  return import(validatorUrl.href);
}

function validRequest() {
  return {
    approved_copy: {
      hero: {
        text: "Evidence-led product engineer",
        approval_status: "user_approved",
        fact_ids: ["FACT-001"],
      },
    },
    content_map: {
      order: ["hero"],
      public_contacts: [],
      public_links: [],
    },
    creative_direction: {
      visual_protagonist: "evidence ledger",
      composition_commitment: "asymmetric annotated field notes",
    },
    generated_html:
      '<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{font-family:sans-serif}@media(max-width:700px){main{display:block}}</style></head><body><main><h1>Evidence-led product engineer</h1><p>evidence ledger</p></main></body></html>',
  };
}

test("accepts approved self-contained responsive HTML", async () => {
  const { validatePreviewRequest } = await loadValidator();
  assert.deepEqual(validatePreviewRequest(validRequest()).errors, []);
});

for (const [name, fragment] of [
  ["script", "<script>alert(1)</script>"],
  ["event handler", "<span onmouseover=alert(1)>evidence ledger</span>"],
  ["javascript URL", '<a href="javascript:alert(1)">evidence ledger</a>'],
  ["remote asset", '<img src="https://tracker.example/x.png">'],
  ["meta refresh", '<meta http-equiv="refresh" content="0;url=https://evil.example">'],
  ["remote CSS URL", '<style>body{background:url(https://evil.example/x)}</style>'],
]) {
  test(`rejects ${name}`, async () => {
    const { validatePreviewRequest } = await loadValidator();
    const payload = validRequest();
    payload.generated_html = payload.generated_html.replace("</body>", `${fragment}</body>`);
    assert.equal(validatePreviewRequest(payload).ok, false);
  });
}

test("rejects visible claims outside approved inputs", async () => {
  const { validatePreviewRequest } = await loadValidator();
  const payload = validRequest();
  payload.generated_html = payload.generated_html.replace(
    "</main>",
    "<p>Increased revenue 90%</p></main>",
  );
  assert.match(validatePreviewRequest(payload).errors.join("\n"), /unapproved visible text/);
});

test("rejects an unapproved public email", async () => {
  const { validatePreviewRequest } = await loadValidator();
  const payload = validRequest();
  payload.approved_copy.contact = {
    text: "person@example.com",
    approval_status: "user_approved",
    fact_ids: ["FACT-002"],
  };
  payload.generated_html = payload.generated_html.replace(
    "</main>",
    "<p>person@example.com</p></main>",
  );
  assert.match(validatePreviewRequest(payload).errors.join("\n"), /unauthorized public contact/);
});

test("accepts a public contact only when explicitly authorized", async () => {
  const { validatePreviewRequest } = await loadValidator();
  const payload = validRequest();
  payload.approved_copy.contact = {
    text: "person@example.com",
    approval_status: "user_approved",
    fact_ids: ["FACT-002"],
  };
  payload.content_map.public_contacts = ["person@example.com"];
  payload.generated_html = payload.generated_html.replace(
    "</main>",
    "<p>person@example.com</p></main>",
  );
  assert.equal(validatePreviewRequest(payload).ok, true);
});

test("requires the approved visual protagonist", async () => {
  const { validatePreviewRequest } = await loadValidator();
  const payload = validRequest();
  payload.generated_html = payload.generated_html.replace("evidence ledger", "hero");
  assert.match(validatePreviewRequest(payload).errors.join("\n"), /visual protagonist/);
});

test("requires viewport and mobile media rules", async () => {
  const { validatePreviewRequest } = await loadValidator();
  const payload = validRequest();
  payload.generated_html = payload.generated_html
    .replace('<meta name="viewport" content="width=device-width,initial-scale=1">', "")
    .replace("@media(max-width:700px){main{display:block}}", "");
  assert.match(validatePreviewRequest(payload).errors.join("\n"), /responsive contract/);
});

test("requires reduced-motion fallback when motion is present", async () => {
  const { validatePreviewRequest } = await loadValidator();
  const payload = validRequest();
  payload.generated_html = payload.generated_html.replace(
    "body{font-family:sans-serif}",
    "body{font-family:sans-serif;transition:color .2s}",
  );
  assert.match(validatePreviewRequest(payload).errors.join("\n"), /reduced-motion/);
});

test("rejects the prohibited generic portfolio stack", async () => {
  const { validatePreviewRequest } = await loadValidator();
  const payload = validRequest();
  payload.generated_html = payload.generated_html.replace(
    "<main>",
    '<main class="gradient-hero skills-grid timeline contact-cta">',
  );
  assert.match(validatePreviewRequest(payload).errors.join("\n"), /generic portfolio stack/);
});

test("the competition example is a valid preview request", async () => {
  const { validatePreviewRequest } = await loadValidator();
  const fixtureUrl = new URL(
    "../../../competition/xinghuo-cup-mvp/contracts/preview-request.example.json",
    import.meta.url,
  );
  assert.equal(existsSync(fixtureUrl), true, "preview request example is missing");
  const payload = JSON.parse(readFileSync(fixtureUrl, "utf8"));
  assert.deepEqual(validatePreviewRequest(payload).errors, []);
});
