// For: Application splash screen supervising engine health and model warm-up
// Must never: Proceed to login while local engine health checks report failure

import React, { useEffect, useState } from "react";
import { advsApi } from "../services/api-client";

interface SplashProps {
  onReady: () => void;
}

export const SplashScreen: React.FC<SplashProps> = ({ onReady }) => {
  const [statusText, setStatusText] = useState("Checking engine status...");
  const [hasError, setHasError] = useState(false);
  const [progress, setProgress] = useState(25);

  const checkHealth = async () => {
    setHasError(false);
    setStatusText("Verifying engine health on 127.0.0.1...");
    setProgress(40);
    try {
      const health = await advsApi.getHealth();
      if (health.status === "healthy") {
        setProgress(80);
        setStatusText("Warming up verification models...");
        setTimeout(() => {
          setProgress(100);
          setStatusText("Engine ready.");
          setTimeout(onReady, 400);
        }, 500);
      } else {
        setHasError(true);
        setStatusText("Engine reported degraded status.");
      }
    } catch {
      setHasError(true);
      setStatusText("Unable to connect to local engine. Ensure background service is running.");
    }
  };

  useEffect(() => {
    checkHealth();
  }, []);

  return (
    <div
      className="grid-blueprint"
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        height: "100vh",
      }}
    >
      <div
        className="wireframe-sheet"
        style={{
          width: 480,
          padding: "40px 36px",
          textAlign: "center",
        }}
      >
        <div style={{ marginBottom: 16 }}>
          <span className="badge-lock">🔒 Air-Gapped & Offline</span>
        </div>

        <h1 className="editorial-hero" style={{ fontSize: 32, marginBottom: 10 }}>
          RAC ADVS
        </h1>

        <div className="editorial-sub" style={{ fontSize: 15, marginBottom: 8 }}>
          Automated Document Verification System
        </div>

        <p className="editorial-body" style={{ marginBottom: 28 }}>
          Recruitment & Assessment Centre, DRDO. Three Sigma precision in &le; 3.0s with complete cryptographic privacy.
        </p>

        <div
          style={{
            height: 6,
            width: "100%",
            backgroundColor: "#E8ECEA",
            borderRadius: 9999,
            overflow: "hidden",
            marginBottom: 16,
          }}
        >
          <div
            style={{
              height: "100%",
              width: `${progress}%`,
              backgroundColor: hasError ? "var(--stamp)" : "var(--ink)",
              transition: "width 0.3s ease",
            }}
          />
        </div>

        <div style={{ fontSize: 13, fontWeight: 500, color: hasError ? "var(--stamp)" : "var(--steel)", marginBottom: 20 }}>
          {statusText}
        </div>

        {hasError && (
          <button
            onClick={checkHealth}
            style={{
              padding: "10px 20px",
              backgroundColor: "var(--ink)",
              color: "#FFF",
              border: "none",
              borderRadius: "9999px",
              fontWeight: 600,
            }}
          >
            Retry connection
          </button>
        )}
      </div>
    </div>
  );
};
