// For: Electron preload context bridge exposing isolated secure API primitives
// Must never: Expose Node.js fs, child_process, or raw IPC listeners to the renderer

import { contextBridge, ipcRenderer } from "electron";

contextBridge.exposeInMainWorld("advsDesktop", {
  platform: process.platform,
  getEnginePort: () => ipcRenderer.invoke("get-engine-port"),
  getEngineToken: () => ipcRenderer.invoke("get-engine-token"),
  onEngineStatus: (callback: (status: string) => void) => {
    ipcRenderer.on("engine-status", (_event, val) => callback(val));
  },
});
