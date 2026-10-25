// For: React client DOM root mounting and strict rendering entry point
// Must never: Execute unauthorized network telemetry on initial mount

import React from "react";
import ReactDOM from "react-dom/client";
import { App } from "./App";
import "./styles/tokens.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
