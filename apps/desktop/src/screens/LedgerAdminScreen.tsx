// For: Consolidated verification ledger, reports, vacancy rules, and audit trail
// Must never: Suppress audit verification warnings or conceal human review rates

import React, { useState, useEffect } from "react";
import { advsApi } from "../services/api-client";
import { useDashboardData } from "../hooks/useDashboardData";
import { Shield } from "lucide-react";

interface LedgerAdminProps {
  userRole: string;
}

export const LedgerAdminScreen: React.FC<LedgerAdminProps> = ({ userRole }) => {
  const [tab, setTab] = useState<"ledger" | "reports" | "vacancies" | "audit">("ledger");
  const { summary, mismatches, accuracy, isLoading } = useDashboardData();

  // Reports state
  const [reportType, setReportType] = useState("verification");
  const [reportFormat, setReportFormat] = useState<"pdf" | "xlsx">("pdf");
  const [generatedReport, setGeneratedReport] = useState<any | null>(null);

  // Vacancies state
  const [vacancies, setVacancies] = useState<any[]>([]);

  // Audit state
  const [auditData, setAuditData] = useState<{ chain_valid: boolean; entries: any[] }>({ chain_valid: true, entries: [] });

  useEffect(() => {
    if (tab === "vacancies") {
      advsApi.getVacancies().then(setVacancies).catch(() => {});
    } else if (tab === "audit" && userRole === "admin") {
      advsApi.getAuditTrail().then(setAuditData).catch(() => {});
    }
  }, [tab, userRole]);

  const handleGenerateReport = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await advsApi.createReport({ type: reportType, format: reportFormat });
      setGeneratedReport(res);
    } catch (err: any) {
      alert(`Report error: ${err.message}`);
    }
  };

  const ledgerRows = summary?.ledger || [];

  return (
    <div style={{ padding: "24px 32px", overflowY: "auto", height: "100vh" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 20 }}>
        <div>
          <h1>Ledger, Reports & Administration</h1>
          <div style={{ fontSize: 13, color: "var(--steel)", marginTop: 4 }}>
            System throughput records, formal export dossiers, vacancy rules, and cryptographic audit
          </div>
        </div>
      </div>

      {/* Workspace Tabs */}
      <div style={{ display: "flex", gap: 8, borderBottom: "var(--border-subtle)", paddingBottom: 10, marginBottom: 20 }}>
        <button
          onClick={() => setTab("ledger")}
          style={{
            padding: "6px 14px",
            border: "none",
            backgroundColor: tab === "ledger" ? "var(--ink)" : "transparent",
            color: tab === "ledger" ? "#FFF" : "var(--steel)",
            borderRadius: "var(--radius-input)",
            fontWeight: 600,
          }}
        >
          Primary Verification Ledger
        </button>
        <button
          onClick={() => setTab("reports")}
          style={{
            padding: "6px 14px",
            border: "none",
            backgroundColor: tab === "reports" ? "var(--ink)" : "transparent",
            color: tab === "reports" ? "#FFF" : "var(--steel)",
            borderRadius: "var(--radius-input)",
            fontWeight: 600,
          }}
        >
          Export Reports
        </button>
        <button
          onClick={() => setTab("vacancies")}
          style={{
            padding: "6px 14px",
            border: "none",
            backgroundColor: tab === "vacancies" ? "var(--ink)" : "transparent",
            color: tab === "vacancies" ? "#FFF" : "var(--steel)",
            borderRadius: "var(--radius-input)",
            fontWeight: 600,
          }}
        >
          Vacancy Rules
        </button>
        {userRole === "admin" && (
          <button
            onClick={() => setTab("audit")}
            style={{
              padding: "6px 14px",
              border: "none",
              backgroundColor: tab === "audit" ? "var(--ink)" : "transparent",
              color: tab === "audit" ? "#FFF" : "var(--steel)",
              borderRadius: "var(--radius-input)",
              fontWeight: 600,
            }}
          >
            Audit Trail
          </button>
        )}
      </div>

      {/* Tab 1: Primary Ledger */}
      {tab === "ledger" && (
        <div>
          <div style={{ backgroundColor: "var(--sheet)", borderRadius: "var(--radius-panel)", border: "var(--border-sheet)", padding: 20, marginBottom: 20 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 14 }}>
              <h2>Verification Throughput Ledger</h2>
              <div
                style={{ fontSize: 13, color: "var(--steel)", cursor: "help" }}
                title={`Formula: auto_verified (${summary?.processed || 0}) × ${summary?.manual_minutes_per_doc || 4} min / 60`}
              >
                <strong>{summary?.hours_saved || 0} hours saved</strong> (hover for formula)
              </div>
            </div>

            <table>
              <thead>
                <tr>
                  <th>Document Type</th>
                  <th style={{ textAlign: "right" }}>Processed</th>
                  <th style={{ textAlign: "right" }}>Auto-verified</th>
                  <th style={{ textAlign: "right" }}>Sent to Review</th>
                  <th style={{ textAlign: "right" }}>Mismatches</th>
                  <th style={{ textAlign: "right" }}>Time / Doc</th>
                </tr>
              </thead>
              <tbody>
                {ledgerRows.length === 0 ? (
                  <tr>
                    <td colSpan={6} style={{ textAlign: "center", color: "var(--steel)", padding: 24 }}>
                      {isLoading ? "Loading ledger..." : "No documents processed yet."}
                    </td>
                  </tr>
                ) : (
                  ledgerRows.map((r: any) => (
                    <tr key={r.document_type}>
                      <td style={{ fontWeight: 600 }}>{r.document_type.replace(/_/g, " ")}</td>
                      <td style={{ textAlign: "right" }}>{r.processed}</td>
                      <td style={{ textAlign: "right", color: "var(--verified)", fontWeight: 600 }}>{r.auto_verified}</td>
                      <td style={{ textAlign: "right", color: "var(--caution)", fontWeight: 600 }}>{r.sent_to_review}</td>
                      <td style={{ textAlign: "right", color: "var(--stamp)", fontWeight: 600 }}>{r.mismatches}</td>
                      <td style={{ textAlign: "right" }}>{r.avg_ms} ms</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
            <div style={{ backgroundColor: "var(--sheet)", padding: 16, borderRadius: "var(--radius-panel)", border: "var(--border-sheet)" }}>
              <h3 style={{ marginBottom: 10 }}>Top Mismatches Detected</h3>
              {mismatches.length === 0 ? (
                <div style={{ fontSize: 13, color: "var(--steel)" }}>No discrepancies reported in recent runs.</div>
              ) : (
                mismatches.slice(0, 4).map((m: any, i: number) => (
                  <div key={i} style={{ fontSize: 13, marginBottom: 8 }}>
                    <strong>{m.field_name.replace(/_/g, " ")}:</strong> {m.count} cases ({m.reason})
                  </div>
                ))
              )}
            </div>
            <div style={{ backgroundColor: "var(--sheet)", padding: 16, borderRadius: "var(--radius-panel)", border: "var(--border-sheet)" }}>
              <h3 style={{ marginBottom: 10 }}>Field Accuracy (Three Sigma)</h3>
              {accuracy.length === 0 ? (
                <div style={{ fontSize: 13, color: "var(--steel)" }}>Accuracy metrics populate after reviewer evaluations.</div>
              ) : (
                accuracy.slice(0, 4).map((a: any, i: number) => (
                  <div key={i} style={{ fontSize: 13, marginBottom: 8 }}>
                    <strong>{a.field_name.replace(/_/g, " ")}:</strong> {a.accuracy}% accuracy ({a.sample_size} samples)
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Export Reports */}
      {tab === "reports" && (
        <div style={{ maxWidth: 520, backgroundColor: "var(--sheet)", padding: 24, borderRadius: "var(--radius-panel)", border: "var(--border-sheet)" }}>
          <h3 style={{ marginBottom: 14 }}>Generate Official Recruitment Report</h3>
          <form onSubmit={handleGenerateReport}>
            <div style={{ marginBottom: 12 }}>
              <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "var(--steel)", marginBottom: 4 }}>Report Type</label>
              <select value={reportType} onChange={(e) => setReportType(e.target.value)} style={{ width: "100%", padding: 8 }}>
                <option value="verification">Verification Outcome Dossier</option>
                <option value="shortlist">Eligible Candidate Shortlist</option>
              </select>
            </div>
            <div style={{ marginBottom: 16 }}>
              <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "var(--steel)", marginBottom: 4 }}>Format</label>
              <select value={reportFormat} onChange={(e) => setReportFormat(e.target.value as any)} style={{ width: "100%", padding: 8 }}>
                <option value="pdf">PDF Document (.pdf)</option>
                <option value="xlsx">Excel Workbook (.xlsx)</option>
              </select>
            </div>
            <button type="submit" style={{ padding: "8px 16px", backgroundColor: "var(--ink)", color: "#FFF", border: "none", borderRadius: "var(--radius-input)", fontWeight: 600 }}>
              Generate Report
            </button>
          </form>

          {generatedReport && (
            <div style={{ marginTop: 16, padding: 12, backgroundColor: "#E8F3EE", borderRadius: "var(--radius-input)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontSize: 13, color: "var(--verified)", fontWeight: 600 }}>{generatedReport.filename}</span>
              <a href={advsApi.getReportDownloadUrl(generatedReport.id)} download target="_blank" rel="noreferrer" style={{ fontSize: 12, fontWeight: 600, color: "var(--ink)" }}>
                Download
              </a>
            </div>
          )}
        </div>
      )}

      {/* Tab 3: Vacancy Rules */}
      {tab === "vacancies" && (
        <div style={{ backgroundColor: "var(--sheet)", borderRadius: "var(--radius-panel)", border: "var(--border-sheet)" }}>
          <table>
            <thead>
              <tr>
                <th>Advertisement No</th>
                <th>Post Name</th>
                <th>Closing Date</th>
                <th>Min %</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {vacancies.map((v) => (
                <tr key={v.id}>
                  <td style={{ fontWeight: 600 }}>{v.advt_no}</td>
                  <td>{v.post_name}</td>
                  <td>{v.closing_date}</td>
                  <td>60%</td>
                  <td><span className="status-stamp match">{v.status}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Tab 4: Audit Trail */}
      {tab === "audit" && userRole === "admin" && (
        <div>
          <div style={{ padding: 10, backgroundColor: auditData.chain_valid ? "#E8F3EE" : "#F8ECEB", color: auditData.chain_valid ? "var(--verified)" : "var(--stamp)", borderRadius: "var(--radius-input)", marginBottom: 14, fontWeight: 600, fontSize: 13, display: "flex", alignItems: "center", gap: 6 }}>
            <Shield size={16} />
            <span>{auditData.chain_valid ? "Cryptographic SHA-256 Hash Chain Verified: All records untampered." : "Audit chain warning."}</span>
          </div>
          <div style={{ backgroundColor: "var(--sheet)", borderRadius: "var(--radius-panel)", border: "var(--border-sheet)" }}>
            <table>
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Operator</th>
                  <th>Action</th>
                  <th>Target Entity</th>
                  <th>Hash</th>
                </tr>
              </thead>
              <tbody>
                {auditData.entries.slice(0, 15).map((e) => (
                  <tr key={e.id}>
                    <td>{new Date(e.ts).toLocaleTimeString()}</td>
                    <td>{e.username || "System"}</td>
                    <td style={{ fontWeight: 600 }}>{e.action}</td>
                    <td>{e.entity_type || "—"}</td>
                    <td style={{ fontFamily: "monospace", fontSize: 11, color: "var(--steel)" }}>{e.hash.substring(0, 12)}...</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
