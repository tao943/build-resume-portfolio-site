"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const {spawn} = require("child_process");

function parseArgs(argv) {
  const values = {open: false, foreground: false};
  for (let index = 0; index < argv.length; index += 1) {
    const name = argv[index];
    if (name === "--open" || name === "--foreground") {
      values[name.slice(2)] = true;
      continue;
    }
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

function outputError(category, message) {
  process.stderr.write(`${JSON.stringify({
    type: "launch-error",
    category,
    message,
  })}\n`);
  process.exitCode = 1;
}

function atomicJson(file, payload) {
  const temporary = `${file}.${process.pid}.tmp`;
  fs.writeFileSync(temporary, `${JSON.stringify(payload, null, 2)}\n`, {
    encoding: "utf8",
    mode: 0o600,
  });
  fs.renameSync(temporary, file);
  try {
    fs.chmodSync(file, 0o600);
  } catch {
    // Windows ACLs remain the platform authority.
  }
}

function waitForStartup(child, timeoutMs) {
  return new Promise((resolve, reject) => {
    let buffer = "";
    const timeout = setTimeout(() => {
      reject(new Error("server startup timed out"));
    }, timeoutMs);
    function finish(error, value) {
      clearTimeout(timeout);
      child.stdout.removeAllListeners();
      child.removeListener("exit", onExit);
      if (error) reject(error);
      else resolve(value);
    }
    function onExit(code) {
      finish(new Error(`server exited before startup with code ${code}`));
    }
    child.once("exit", onExit);
    child.stdout.setEncoding("utf8");
    child.stdout.on("data", (chunk) => {
      buffer += chunk;
      const newline = buffer.indexOf("\n");
      if (newline < 0) return;
      const line = buffer.slice(0, newline);
      try {
        finish(null, JSON.parse(line));
      } catch (error) {
        finish(new Error(`invalid server startup JSON: ${error.message}`));
      }
    });
  });
}

function browserCommand(url) {
  if (process.env.VISUAL_COMPANION_OPEN_COMMAND) {
    return {
      command: process.env.VISUAL_COMPANION_OPEN_COMMAND,
      args: [url],
    };
  }
  if (process.platform === "win32") {
    return {
      command: "powershell.exe",
      args: [
        "-NoProfile",
        "-NonInteractive",
        "-Command",
        "Start-Process -FilePath $args[0]",
        url,
      ],
    };
  }
  if (process.platform === "darwin") {
    return {command: "open", args: [url]};
  }
  return {command: "xdg-open", args: [url]};
}

function openBrowser(url) {
  return new Promise((resolve) => {
    const launcher = browserCommand(url);
    let settled = false;
    const child = spawn(launcher.command, launcher.args, {
      detached: false,
      stdio: "ignore",
      windowsHide: true,
    });
    function done(value) {
      if (settled) return;
      settled = true;
      resolve(value);
    }
    child.once("error", () => done("OPEN_FAILED"));
    child.once("spawn", () => {
      child.unref();
      done(null);
    });
  });
}

async function main() {
  let args;
  try {
    args = parseArgs(process.argv.slice(2));
  } catch (error) {
    outputError("INVALID_ARGUMENT", error.message);
    return;
  }
  if (!args["workspace-root"] || !args.gallery) {
    outputError(
      "INVALID_ARGUMENT",
      "workspace-root and gallery are required",
    );
    return;
  }

  const workspaceRoot = path.resolve(args["workspace-root"]);
  const sourceGallery = path.resolve(args.gallery);
  let sourceStat;
  try {
    sourceStat = fs.lstatSync(sourceGallery);
  } catch (error) {
    outputError("INVALID_PREVIEW_PATH", error.message);
    return;
  }
  if (
    sourceStat.isSymbolicLink()
    || !sourceStat.isFile()
    || path.extname(sourceGallery).toLowerCase() !== ".html"
  ) {
    outputError(
      "INVALID_PREVIEW_PATH",
      "gallery must be a regular HTML file",
    );
    return;
  }

  const sessionsRoot = path.join(
    workspaceRoot,
    ".resume-site-work",
    "style-preview",
    "sessions",
  );
  fs.mkdirSync(sessionsRoot, {recursive: true});
  const sessionDir = fs.mkdtempSync(path.join(sessionsRoot, "style-"));
  const stateDir = path.join(sessionDir, "state");
  fs.mkdirSync(stateDir);
  const gallery = path.join(sessionDir, "gallery.html");
  fs.copyFileSync(sourceGallery, gallery);
  const sourceAssets = path.join(path.dirname(sourceGallery), "assets");
  if (fs.existsSync(sourceAssets) && fs.lstatSync(sourceAssets).isDirectory()) {
    fs.cpSync(sourceAssets, path.join(sessionDir, "assets"), {
      recursive: true,
      errorOnExist: true,
    });
  }

  const token = crypto.randomBytes(32).toString("hex");
  const serverScript = path.join(__dirname, "server.cjs");
  const logPath = path.join(stateDir, "server.log");
  const logFd = fs.openSync(logPath, "a", 0o600);
  const child = spawn(
    process.execPath,
    [
      serverScript,
      "--session-dir",
      sessionDir,
      "--gallery",
      gallery,
      "--host",
      args.host || "127.0.0.1",
      "--port",
      args.port || "0",
      "--token",
      token,
    ],
    {
      cwd: sessionDir,
      detached: !args.foreground,
      stdio: ["ignore", "pipe", logFd],
      windowsHide: true,
    },
  );
  fs.closeSync(logFd);

  let startup;
  try {
    startup = await waitForStartup(child, 5000);
  } catch (error) {
    if (child.exitCode === null) child.kill();
    outputError("SERVER_REAPED", error.message);
    return;
  }

  let openWarning = null;
  if (args.open) openWarning = await openBrowser(startup.url);
  const serverInfoPath = path.join(stateDir, "server-info.json");
  const info = {
    ...startup,
    server_info: serverInfoPath,
    open_warning: openWarning,
  };
  atomicJson(serverInfoPath, info);
  process.stdout.write(`${JSON.stringify(info)}\n`);

  if (args.foreground) {
    child.stdout.resume();
    await new Promise((resolve) => child.once("exit", resolve));
  } else {
    child.stdout.destroy();
    child.unref();
  }
}

main().catch((error) => {
  outputError("LAUNCH_FAILED", error.message);
});
