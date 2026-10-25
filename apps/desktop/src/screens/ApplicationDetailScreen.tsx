// For: Comprehensive single-applicant profile and attached document verification status
// Must never: Recompute eligibility without displaying rule reasons to the officer

import React, { useState, useEffect } from "react";
import { advsApi } from "../services/api-client";
import { ArrowLeft } from "lucide-react";

interface AppDetailProps {
  applicationId: string;
  onBack: () => void;
  onOpenWorkbench: (docId: string) => void;
}

export const ApplicationDetailScreen: React.FC<AppDetailProps> = ({
  applicationId,
  onBack,
  onOpenWorkbench,
}) => {
  const [app, setApp] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [alerts, setAlerts] = useState<any[]>([]);

  const loadDetail = async () => {
    setIsLoading(true);
    try {
      const data = await advsApi.getApplication(applicationId);
      setApp(data);
    } catch {
      // Error handled silently
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDetail();
  }, [applicationId]);

  const handleEvaluateEligibility = async () => {
    try {
      await advsApi.evaluateApplicationEligibility(applicationId);
      loadDetail();
    } catch (err: any) {
      alert(`Evaluation error: ${err.message}`);
    }
  };

  const handleExportAlerts = async () => {
    try {
      const res = await advsApi.exportApplicationAlerts(applicationId);
      setAlerts(res.alerts);
    } catch (err: any) {
      alert(`Alert export error: ${err.message}`);
    }
  };

  if (isLoading || !app) {
    return <div style={{ padding: 32, color: "var(--steel)" }}>Loading application record...</div>;
  }

  const biodata = typeof app.biodata_json === "string" ? JSON.parse(app.biodata_json) : app.biodata_json;
  const docs = app.documents || [];

  return (
    <div style={{ padding: "24px 32px", overflowY: "auto", height: "100vh" }}>
      <button
        onClick={onBack}
        style={{ display: "flex", alignItems: "center", gap: 6, background: "none", border: "none", color: "var(--steel)", marginBottom: 14, cursor: "pointer" }}
      >
        <ArrowLeft size={16} />
        <span>Back to applications</span>
      </button>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 20 }}>
        <div>
          <h1>{app.full_name}</h1>
          <div style={{ fontSize: 13, color: "var(--steel)", marginTop: 4 }}>
            Registration No: <strong>{app.registration_no}</strong> &bull; Applied Category: <strong>{app.category || "UR"}</strong>
          </div>
        </div>

        <div style={{ display: "flex", gap: 10 }}>
          <button
            onClick={handleEvaluateEligibility}
            style={{ padding: "8px 14px", border: "1px solid var(--steel)", backgroundColor: "var(--sheet)", borderRadius: "var(--radius-input)", fontWeight: 600 }}
          >
            Evaluate eligibility
          </button>
          <button
            onClick={handleExportAlerts}
            style={{ padding: "8px 14px", backgroundColor: "var(--ink)", color: "#FFF", border: "none", borderRadius: "var(--radius-input)", fontWeight: 600 }}
          >
            Export mismatch alert
          </button>
        </div>
      </div>

      {alerts.length > 0 && (
        <div style={{ padding: 14, backgroundColor: "#F8ECEB", border: "1px solid var(--stamp)", borderRadius: "var(--radius-panel)", marginBottom: 20 }}>
          <div style={{ fontWeight: 600, color: "var(--stamp)", marginBottom: 4 }}>Applicant discrepancy notification text</div>
          {alerts.map((alt: any, i: number) => (
            <div key={i} style={{ fontSize: 13, color: "var(--ink)" }}>&bull; {alt.message}</div>
          ))}
        </div>
      )}

      {/* Two Column Layout: Biodata vs Attached Documents */}
      <div style={{ display: "grid", gridTemplateColumns: "360px 1fr", gap: 24 }}>
        {/* Biodata summary */}
        <div style={{ backgroundColor: "var(--sheet)", padding: 20, borderRadius: "var(--radius-panel)", border: "var(--border-sheet)" }}>
          <h3 style={{ marginBottom: 12 }}>Submitted biodata</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: 8, fontSize: 13 }}>
            <div><span style={{ color: "var(--steel)" }}>Father's Name:</span> {app.father_name || "—"}</div>
            <div><span style={{ color: "var(--steel)" }}>Date of Birth:</span> {app.dob || "—"}</div>
            <div><span style={{ color: "var(--steel)" }}>Degree:</span> {biodata?.qualification?.degree || "—"}</div>
            <div><span style={{ color: "var(--steel)" }}>Branch:</span> {biodata?.qualification?.branch || "—"}</div>
            <div><span style={{ color: "var(--steel)" }}>Percentage:</span> {biodata?.qualification?.percentage || "—"}%</div>
            <div><span style={{ color: "var(--steel)" }}>GATE Score:</span> {biodata?.gate?.score || "—"}</div>
            <div><span style={{ color: "var(--steel)" }}>Eligibility:</span> <strong style={{ textTransform: "capitalize" }}>{app.eligibility}</strong></div>
          </div>
        </div>

        {/* Attached Documents Table */}
        <div style={{ backgroundColor: "var(--sheet)", padding: 20, borderRadius: "var(--radius-panel)", border: "var(--border-sheet)" }}>
          <h3 style={{ marginBottom: 12 }}>Attached supporting documents</h3>
          <table>
            <thead>
              <tr>
                <th>Document Name</th>
                <th>Type</th>
                <th>Verification status</th>
                <th style={{ textAlign: "right" }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {docs.length === 0 ? (
                <tr>
                  <td colSpan={4} style={{ textAlign: "center", color: "var(--steel)", padding: 24 }}>
                    No documents uploaded for this applicant.
                  </td>
                </tr>
              ) : (
                docs.map((doc: any) => (
                  <tr key={doc.id}>
                    <td style={{ fontWeight: 600 }}>{doc.original_filename}</td>
                    <td style={{ textTransform: "capitalize" }}>{doc.detected_type?.replace(/_/g, " ") || "Uploaded"}</td>
                    <td>
                      <span className={`status-stamp ${doc.status === "verified" ? "match" : doc.status === "needs_review" ? "caution" : "mismatch"}`}>
                        {doc.status}
                      </span>
                    </td>
                    <td style={{ textAlign: "right" }}>
                      <button
                        onClick={() => onOpenWorkbench(doc.id)}
                        style={{ padding: "4px 8px", background: "none", border: "1px solid var(--steel)", borderRadius: "var(--radius-input)" }}
                      >
                        Inspect in workbench
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
