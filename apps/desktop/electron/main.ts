// For: Electron main process lifecycle, window creation, and Python engine supervision
// Must never: Disable context isolation, enable node integration, or allow remote content

import { app, BrowserWindow, ipcMain } from "electron";
import { spawn, ChildProcess } from "child_process";
import * as path from "path";
import * as crypto from "crypto";

import * as fs from "fs";

let mainWindow: BrowserWindow | null = null;
let engineProcess: ChildProcess | null = null;
const enginePort = process.env.ADVS_ENGINE_PORT || "8000";
const launchToken = crypto.randomBytes(24).toString("hex");

function resolveEngineExecution(): { cmd: string; args: string[]; cwd: string } {
  const isPackaged = app.isPackaged;
  const bundled = path.join(process.resourcesPath, "engine", "advs-engine", "advs-engine");
  const direct = path.join(process.resourcesPath, "advs-engine", "advs-engine");

  if (isPackaged && fs.existsSync(bundled)) {
    return { cmd: bundled, args: [], cwd: path.dirname(bundled) };
  }
  if (isPackaged && fs.existsSync(direct)) {
    return { cmd: direct, args: [], cwd: path.dirname(direct) };
  }

  const engineDir = path.resolve(__dirname, "../../engine");
  const pythonPath = process.platform === "win32"
    ? path.join(engineDir, ".venv", "Scripts", "python.exe")
    : path.join(engineDir, ".venv", "bin", "python");

  return {
    cmd: pythonPath,
    args: ["-m", "uvicorn", "engine.app.main:app", "--host", "127.0.0.1", "--port", enginePort],
    cwd: path.resolve(__dirname, "../.."),
  };
}

function startEngine() {
  const { cmd, args, cwd } = resolveEngineExecution();
  const userDataDir = app.getPath("userData");

  engineProcess = spawn(cmd, args, {
    cwd,
    env: {
      ...process.env,
      ADVS_ENGINE_PORT: enginePort,
      ADVS_LAUNCH_TOKEN: launchToken,
      ADVS_DATA_DIR: path.join(userDataDir, "data"),
      PYTHONPATH: path.resolve(__dirname, "../.."),
    },
  });

  engineProcess.on("error", (err) => {
    console.warn("ADVS engine spawn note:", err.message);
  });

  engineProcess.on("exit", (code) => {
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send("engine-status", `exited_${code}`);
    }
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1360,
    height: 820,
    minWidth: 1280,
    minHeight: 720,
    backgroundColor: "#E8ECEA",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });

  if (process.env.VITE_DEV_SERVER_URL) {
    mainWindow.loadURL(process.env.VITE_DEV_SERVER_URL);
  } else {
    mainWindow.loadFile(path.join(__dirname, "../dist/index.html"));
  }
}

app.whenReady().then(() => {
  ipcMain.handle("get-engine-port", () => enginePort);
  ipcMain.handle("get-engine-token", () => launchToken);

  startEngine();
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  if (engineProcess) {
    engineProcess.kill();
  }
  if (process.platform !== "darwin") {
    app.quit();
  }
});
