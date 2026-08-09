const REQUIRED_FIELDS = [
  "approved_copy",
  "content_map",
  "creative_direction",
  "generated_html",
];

const FORBIDDEN_HTML = [
  [/<\s*script\b/i, "script element"],
  [/<\s*(?:form|iframe|object|embed|svg)\b/i, "active element"],
  [/<\s*(?:img|video|audio|source|link|base)\b/i, "unapproved media element"],
  [/<\s*meta\b[^>]*http-equiv/i, "meta http-equiv"],
  [/\son[a-z]+\s*=/i, "event handler"],
  [/javascript\s*:/i, "javascript URL"],
  [/@import\s+/i, "CSS import"],
  [/url\(\s*["']?https?:/i, "remote CSS URL"],
];

const FIXED_LABELS = ["about", "projects", "experience", "contact"];

function normalizeText(value) {
  return value
    .replace(/&nbsp;/gi, " ")
    .replace(/&amp;/gi, "&")
    .replace(/&lt;/gi, "<")
    .replace(/&gt;/gi, ">")
    .replace(/&quot;/gi, '"')
    .replace(/&#39;/gi, "'")
    .replace(/\s+/g, " ")
    .trim()
    .toLowerCase();
}

function visibleSegments(html) {
  const withoutStyles = html.replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi, " ");
  return [...withoutStyles.matchAll(/>([^<]+)</g)]
    .map((match) => normalizeText(match[1]))
    .filter(Boolean);
}

function collectStrings(value, output = []) {
  if (typeof value === "string") {
    const normalized = normalizeText(value);
    if (normalized) output.push(normalized);
  } else if (Array.isArray(value)) {
    for (const item of value) collectStrings(item, output);
  } else if (value && typeof value === "object") {
    for (const item of Object.values(value)) collectStrings(item, output);
  }
  return output;
}

function stringArray(value) {
  return Array.isArray(value) && value.every((item) => typeof item === "string");
}

function validateApprovedCopy(approvedCopy, errors) {
  if (!approvedCopy || typeof approvedCopy !== "object" || Array.isArray(approvedCopy)) {
    errors.push("approved_copy must be an object");
    return;
  }
  for (const [key, block] of Object.entries(approvedCopy)) {
    if (!block || typeof block !== "object" || Array.isArray(block)) {
      errors.push(`approved_copy.${key} must be an object`);
      continue;
    }
    if (block.approval_status !== "user_approved") {
      errors.push(`approved_copy.${key} is not user approved`);
    }
    if (!stringArray(block.fact_ids) || block.fact_ids.length === 0) {
      errors.push(`approved_copy.${key} has no fact IDs`);
    } else if (block.fact_ids.some((factId) => !/^FACT-\d{3,}$/.test(factId))) {
      errors.push(`approved_copy.${key} contains an invalid fact ID`);
    }
    if (typeof block.text !== "string" || !block.text.trim()) {
      errors.push(`approved_copy.${key} has no visible text`);
    }
  }
}

function validateContacts(visibleText, contentMap, errors) {
  const authorized = new Set(
    stringArray(contentMap.public_contacts)
      ? contentMap.public_contacts.map((value) => normalizeText(value))
      : [],
  );
  const contacts =
    visibleText.match(
      /[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}|(?:\+?86[- ]?)?1[3-9](?:[- ]?\d){9}/gi,
    ) || [];
  if (contacts.some((value) => !authorized.has(normalizeText(value)))) {
    errors.push("unauthorized public contact detected");
  }
}

function validateLinks(html, contentMap, errors) {
  const authorized = new Set(
    stringArray(contentMap.public_links) ? contentMap.public_links : [],
  );
  const links = [...html.matchAll(/<a\b[^>]*\shref\s*=\s*["']([^"']+)["']/gi)].map(
    (match) => match[1],
  );
  if (links.some((value) => !value.startsWith("#") && !authorized.has(value))) {
    errors.push("unauthorized public link detected");
  }
}

function validateHtml(payload, errors) {
  const html = payload.generated_html;
  if (typeof html !== "string" || !html.trim()) {
    errors.push("generated_html must be a non-empty string");
    return;
  }
  if (!/^<!doctype html>/i.test(html.trim())) {
    errors.push("generated_html must be a complete HTML document");
  }
  if (!/<html\b/i.test(html) || !/<body\b/i.test(html) || !/<main\b/i.test(html)) {
    errors.push("generated_html requires html, body, and main elements");
  }
  for (const [pattern, label] of FORBIDDEN_HTML) {
    if (pattern.test(html)) errors.push(`forbidden HTML pattern: ${label}`);
  }

  const visible = visibleSegments(html);
  const allowed = collectStrings([
    payload.approved_copy,
    payload.content_map,
    payload.creative_direction,
    FIXED_LABELS,
  ]);
  if (!visible.every((segment) => allowed.some((source) => source.includes(segment)))) {
    errors.push("unapproved visible text detected");
  }

  const visibleJoined = visible.join(" ");
  validateContacts(visibleJoined, payload.content_map, errors);
  validateLinks(html, payload.content_map, errors);

  const protagonist = normalizeText(payload.creative_direction.visual_protagonist || "");
  if (!protagonist || !visibleJoined.includes(protagonist)) {
    errors.push("visual protagonist is not observable");
  }

  if (!/<meta\s+name=["']?viewport["']?/i.test(html) || !/@media\s*\(/i.test(html)) {
    errors.push("responsive contract is missing");
  }

  if (/(?:animation|transition)\s*:/i.test(html) && !/prefers-reduced-motion/i.test(html)) {
    errors.push("motion requires a prefers-reduced-motion fallback");
  }

  const lowered = html.toLowerCase();
  if (
    ["gradient-hero", "skills-grid", "timeline", "contact-cta"].every((marker) =>
      lowered.includes(marker),
    )
  ) {
    errors.push("prohibited generic portfolio stack detected");
  }

  const repeatedCards = [...html.matchAll(/class\s*=\s*["'][^"']*\bcard\b[^"']*["']/gi)].length;
  if (repeatedCards >= 3) {
    errors.push("projects collapse into repeated generic cards");
  }
}

export function validatePreviewRequest(payload) {
  const errors = [];
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
    return { ok: false, errors: ["payload must be an object"], normalized: null };
  }
  for (const field of REQUIRED_FIELDS) {
    if (!(field in payload)) errors.push(`missing field: ${field}`);
  }
  if (errors.length > 0) return { ok: false, errors, normalized: null };

  validateApprovedCopy(payload.approved_copy, errors);
  if (!payload.content_map || typeof payload.content_map !== "object") {
    errors.push("content_map must be an object");
  }
  if (!payload.creative_direction || typeof payload.creative_direction !== "object") {
    errors.push("creative_direction must be an object");
  }
  if (errors.length === 0) validateHtml(payload, errors);

  return {
    ok: errors.length === 0,
    errors,
    normalized: errors.length === 0 ? structuredClone(payload) : null,
  };
}
