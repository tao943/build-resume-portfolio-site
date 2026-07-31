"use strict";

const fs = require("fs");
const http = require("http");
const path = require("path");

function parseArgs(argv) {
  const values = {};
  for (let index = 0; index < argv.length; index += 1) {
    const name = argv[index];
    const value = argv[index + 1];
    if (
      !name.startsWith("--")
      || value === undefined
      || value.startsWith("--")
    ) {
      throw new Error(`invalid argument near ${name}`);
    }
    values[name.slice(2)] = value;
    index += 1;
  }
  return values;
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

function outputError(category, message) {
  process.stderr.write(`${JSON.stringify({
    type: "stop-error",
    category,
    message,
  })}\n`);
  process.exitCode = 1;
}

function healthUrl(url) {
  const target = new URL(url);
  target.pathname = "/health";
  return target;
}

function readHealth(url, timeoutMs = 1500) {
  return new Promise((resolve, reject) => {
    const request = http.get(url, (response) => {
      let body = "";
      response.setEncoding("utf8");
      response.on("data", (chunk) => {
        body += chunk;
      });
      response.on("end", () => {
        if (response.statusCode !== 200) {
          reject(new Error(`health returned ${response.statusCode}`));
          return;
        }
        try {
          resolve(JSON.parse(body));
        } catch (error) {
          reject(error);
        }
      });
    });
    request.setTimeout(timeoutMs, () => {
      request.destroy(new Error("health timed out"));
    });
    request.once("error", reject);
  });
}

function delay(milliseconds) {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

async function main() {
  let args;
  try {
    args = parseArgs(process.argv.slice(2));
  } catch (error) {
    outputError("INVALID_ARGUMENT", error.message);
    return;
  }
  if (!args["workspace-root"] || !args["server-info"]) {
    outputError(
      "INVALID_ARGUMENT",
      "workspace-root and server-info are required",
    );
    return;
  }

  const workspaceRoot = path.resolve(args["workspace-root"]);
  const sessionsRoot = path.resolve(
    workspaceRoot,
    ".resume-site-work",
    "style-preview",
    "sessions",
  );
  const serverInfoPath = path.resolve(args["server-info"]);
  if (
    !isInside(sessionsRoot, serverInfoPath)
    || path.basename(serverInfoPath) !== "server-info.json"
    || path.basename(path.dirname(serverInfoPath)) !== "state"
  ) {
    outputError(
      "INVALID_SESSION_PATH",
      "server-info must belong to the workspace sessions directory",
    );
    return;
  }

  let info;
  try {
    info = JSON.parse(fs.readFileSync(serverInfoPath, "utf8"));
  } catch (error) {
    outputError("INVALID_SERVER_INFO", error.message);
    return;
  }
  const sessionDir = path.resolve(info.session_dir || "");
  const expectedSession = path.dirname(path.dirname(serverInfoPath));
  if (
    sessionDir !== expectedSession
    || !isInside(sessionsRoot, sessionDir)
    || !Number.isInteger(info.pid)
    || typeof info.url !== "string"
  ) {
    outputError("INVALID_SERVER_INFO", "server identity is inconsistent");
    return;
  }

  let health;
  try {
    health = await readHealth(healthUrl(info.url));
  } catch (error) {
    outputError("SERVER_NOT_VERIFIED", error.message);
    return;
  }
  if (
    health.pid !== info.pid
    || path.resolve(health.session_dir || "") !== sessionDir
  ) {
    outputError("SERVER_NOT_VERIFIED", "health identity does not match");
    return;
  }

  try {
    process.kill(info.pid, "SIGTERM");
  } catch (error) {
    outputError("STOP_FAILED", error.message);
    return;
  }
  for (let attempt = 0; attempt < 30; attempt += 1) {
    await delay(100);
    try {
      await readHealth(healthUrl(info.url), 200);
    } catch {
      process.stdout.write(`${JSON.stringify({
        type: "server-stopped",
        pid: info.pid,
        session_dir: sessionDir,
      })}\n`);
      return;
    }
  }
  outputError("STOP_FAILED", "server did not stop within three seconds");
}

main().catch((error) => {
  outputError("STOP_FAILED", error.message);
});
