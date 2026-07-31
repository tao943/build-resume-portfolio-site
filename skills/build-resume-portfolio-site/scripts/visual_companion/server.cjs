"use strict";

const crypto = require("crypto");
const fs = require("fs");
const http = require("http");
const path = require("path");

const MIME = new Map([
  [".html", "text/html; charset=utf-8"],
  [".css", "text/css; charset=utf-8"],
  [".js", "application/javascript; charset=utf-8"],
  [".json", "application/json; charset=utf-8"],
  [".svg", "image/svg+xml"],
  [".png", "image/png"],
  [".jpg", "image/jpeg"],
  [".jpeg", "image/jpeg"],
  [".webp", "image/webp"],
  [".gif", "image/gif"],
]);

function parseArgs(argv) {
  const values = {};
  for (let index = 0; index < argv.length; index += 1) {
    const name = argv[index];
    if (!name.startsWith("--")) {
      throw new Error(`unexpected argument: ${name}`);
    }
    const value = argv[index + 1];
    if (value === undefined || value.startsWith("--")) {
      throw new Error(`missing value for ${name}`);
    }
    values[name.slice(2)] = value;
    index += 1;
  }
  return values;
}

function safeEqual(left, right) {
  const first = Buffer.from(String(left));
  const second = Buffer.from(String(right));
  return (
    first.length === second.length
    && crypto.timingSafeEqual(first, second)
  );
}

function isInside(root, target) {
  const relative = path.relative(root, target);
  return (
    relative === ""
    || (
      relative !== ".."
      && !relative.startsWith(`..${path.sep}`)
      && !path.isAbsolute(relative)
    )
  );
}

function cookieValue(header, name) {
  if (!header) return null;
  for (const part of header.split(";")) {
    const [key, ...rest] = part.trim().split("=");
    if (key === name) return rest.join("=");
  }
  return null;
}

function securityHeaders(extra = {}) {
  return {
    "Cache-Control": "no-store",
    "Content-Security-Policy": [
      "default-src 'self'",
      "style-src 'self' 'unsafe-inline'",
      "img-src 'self' data:",
      "font-src 'self' data:",
      "script-src 'none'",
      "object-src 'none'",
      "base-uri 'none'",
      "frame-ancestors 'none'",
    ].join("; "),
    "Cross-Origin-Resource-Policy": "same-origin",
    "Referrer-Policy": "no-referrer",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    ...extra,
  };
}

function fail(category, message) {
  process.stderr.write(`${JSON.stringify({
    type: "server-error",
    category,
    message,
  })}\n`);
  process.exitCode = 1;
}

let args;
try {
  args = parseArgs(process.argv.slice(2));
} catch (error) {
  fail("INVALID_ARGUMENT", error.message);
  return;
}

const host = args.host || "127.0.0.1";
const port = Number(args.port || "0");
const token = args.token || "";
if (!Number.isInteger(port) || port < 0 || port > 65535) {
  fail("INVALID_ARGUMENT", "port must be an integer from 0 to 65535");
  return;
}
if (token.length < 16) {
  fail("INVALID_ARGUMENT", "token must contain at least 16 characters");
  return;
}
if (!args["session-dir"] || !args.gallery) {
  fail("INVALID_ARGUMENT", "session-dir and gallery are required");
  return;
}

let sessionRoot;
let galleryPath;
try {
  sessionRoot = fs.realpathSync(path.resolve(args["session-dir"]));
  galleryPath = fs.realpathSync(path.resolve(args.gallery));
  const galleryStat = fs.lstatSync(galleryPath);
  if (
    !isInside(sessionRoot, galleryPath)
    || galleryStat.isSymbolicLink()
    || !galleryStat.isFile()
    || path.extname(galleryPath).toLowerCase() !== ".html"
  ) {
    throw new Error("gallery must be a regular HTML file inside session-dir");
  }
} catch (error) {
  fail("INVALID_PREVIEW_PATH", error.message);
  return;
}

const cookieName = `visual-preview-key-${crypto
  .createHash("sha256")
  .update(token)
  .digest("hex")
  .slice(0, 12)}`;

function authorized(requestUrl, request) {
  const queryKey = requestUrl.searchParams.get("key");
  const cookieKey = cookieValue(request.headers.cookie, cookieName);
  return safeEqual(queryKey || cookieKey || "", token);
}

function regularAllowedFile(target) {
  try {
    const realTarget = fs.realpathSync(target);
    const stat = fs.lstatSync(target);
    return (
      isInside(sessionRoot, realTarget)
      && stat.isFile()
      && !stat.isSymbolicLink()
      && MIME.has(path.extname(realTarget).toLowerCase())
    )
      ? realTarget
      : null;
  } catch {
    return null;
  }
}

function responseFile(request, response, target) {
  const data = fs.readFileSync(target);
  const contentType = MIME.get(path.extname(target).toLowerCase());
  response.writeHead(200, securityHeaders({
    "Content-Length": String(data.length),
    "Content-Type": contentType,
  }));
  if (request.method === "HEAD") response.end();
  else response.end(data);
}

const server = http.createServer((request, response) => {
  if (!["GET", "HEAD"].includes(request.method)) {
    response.writeHead(405, securityHeaders({
      Allow: "GET, HEAD",
      "Content-Type": "text/plain; charset=utf-8",
    }));
    response.end("Method not allowed");
    return;
  }

  const base = `http://${request.headers.host || `${host}:${port}`}`;
  let requestUrl;
  try {
    requestUrl = new URL(request.url, base);
  } catch {
    response.writeHead(400, securityHeaders());
    response.end("Bad request");
    return;
  }
  if (!authorized(requestUrl, request)) {
    response.writeHead(403, securityHeaders({
      "Content-Type": "text/plain; charset=utf-8",
    }));
    response.end("Forbidden");
    return;
  }

  if (requestUrl.searchParams.has("key")) {
    response.setHeader(
      "Set-Cookie",
      `${cookieName}=${token}; HttpOnly; SameSite=Strict; Path=/`,
    );
  }

  if (requestUrl.pathname === "/") {
    responseFile(request, response, galleryPath);
    return;
  }
  if (requestUrl.pathname.startsWith("/files/")) {
    let relative;
    try {
      relative = decodeURIComponent(requestUrl.pathname.slice(7));
    } catch {
      relative = "";
    }
    const target = regularAllowedFile(path.resolve(sessionRoot, relative));
    if (target) {
      responseFile(request, response, target);
      return;
    }
  }
  response.writeHead(404, securityHeaders({
    "Content-Type": "text/plain; charset=utf-8",
  }));
  response.end("Not found");
});

server.on("error", (error) => {
  fail(
    error.code === "EADDRINUSE" ? "PORT_BIND_FAILED" : "SERVER_FAILED",
    error.message,
  );
});

function stop() {
  server.close(() => process.exit(0));
}
process.on("SIGINT", stop);
process.on("SIGTERM", stop);

server.listen(port, host, () => {
  const address = server.address();
  const activePort = address.port;
  const url = `http://${host}:${activePort}/?key=${encodeURIComponent(token)}`;
  process.stdout.write(`${JSON.stringify({
    type: "server-started",
    pid: process.pid,
    port: activePort,
    host,
    url,
    session_dir: sessionRoot,
    gallery: galleryPath,
  })}\n`);
});
