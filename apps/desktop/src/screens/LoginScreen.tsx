// For: Operator authentication screen with credential submission and error banner
// Must never: Store plaintext passwords in component state or bypass lockout notices

import React, { useState } from "react";
import { advsApi, setAuthToken } from "../services/api-client";

interface LoginProps {
  onLoginSuccess: (user: { id: string; username: string; name: string; role: string }) => void;
}

export const LoginScreen: React.FC<LoginProps> = ({ onLoginSuccess }) => {
  const [username, setUsername] = useState("officer1");
  const [password, setPassword] = useState("Officer@123");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    setIsSubmitting(true);
    try {
      const res = await advsApi.login({ username, password });
      setAuthToken(res.access_token);
      onLoginSuccess(res.user);
    } catch (err: any) {
      setErrorMessage(err.message || "Invalid credentials. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      className="grid-blueprint"
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        height: "100vh",
      }}
    >
      <div
        className="wireframe-sheet"
        style={{
          width: 440,
          padding: "36px 32px",
        }}
      >
        <div style={{ marginBottom: 12 }}>
          <span className="badge-lock">🔒 DRDO RAC Authenticated Portal</span>
        </div>

        <h1 className="editorial-hero" style={{ fontSize: 26, marginBottom: 6 }}>
          Verification Desk
        </h1>
        <div className="editorial-body" style={{ marginBottom: 20 }}>
          Recruitment & Assessment Centre. Sign in to access offline screening queues.
        </div>

        {errorMessage && (
          <div
            style={{
              padding: "10px 14px",
              backgroundColor: "#F8ECEB",
              border: "1px solid var(--stamp)",
              color: "var(--stamp)",
              borderRadius: "8px",
              fontSize: 13,
              marginBottom: 16,
            }}
          >
            {errorMessage}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: 14 }}>
            <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "var(--steel)", marginBottom: 6 }}>
              Username
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              style={{
                width: "100%",
                padding: "9px 12px",
                border: "1px solid #C4CEC8",
                borderRadius: "8px",
                fontSize: 14,
                backgroundColor: "#FFF",
                color: "var(--ink)",
              }}
            />
          </div>

          <div style={{ marginBottom: 20 }}>
            <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "var(--steel)", marginBottom: 6 }}>
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              style={{
                width: "100%",
                padding: "9px 12px",
                border: "1px solid #C4CEC8",
                borderRadius: "8px",
                fontSize: 14,
                backgroundColor: "#FFF",
                color: "var(--ink)",
              }}
            />
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            style={{
              width: "100%",
              padding: "11px",
              backgroundColor: "var(--ink)",
              color: "#FFF",
              border: "none",
              borderRadius: "9999px",
              fontWeight: 600,
              fontSize: 14,
              cursor: isSubmitting ? "not-allowed" : "pointer",
            }}
          >
            {isSubmitting ? "Signing in..." : "Enter Verification Desk ✦"}
          </button>
        </form>

        <div style={{ marginTop: 22, paddingTop: 16, borderTop: "1px solid #E8ECEA", fontSize: 12, color: "var(--steel)" }}>
          <div style={{ marginBottom: 6, fontWeight: 600 }}>1-Click Operator Roles:</div>
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
            <span
              onClick={() => { setUsername("officer1"); setPassword("Officer@123"); }}
              style={{ cursor: "pointer" }}
              className="badge-pill"
            >
              officer1 (Screening)
            </span>
            <span
              onClick={() => { setUsername("reviewer1"); setPassword("Reviewer@123"); }}
              style={{ cursor: "pointer" }}
              className="badge-pill"
            >
              reviewer1 (Workbench)
            </span>
            <span
              onClick={() => { setUsername("admin"); setPassword("Admin@123"); }}
              style={{ cursor: "pointer" }}
              className="badge-pill"
            >
              admin (Audit)
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
