// For: Dashboard ledger display, throughput metrics, and mismatch breakdown charts
// Must never: Place decorative gradient cards above the primary verification ledger

import React from "react";
import { useDashboardData } from "../hooks/useDashboardData";

interface DashboardProps {
  onNavigate: (screen: string) => void;
}

export const DashboardScreen: React.FC<DashboardProps> = ({ onNavigate }) => {
  const { summary, mismatches, accuracy, isLoading, error } = useDashboardData();

  if (isLoading) {
    return <div style={{ padding: 24, color: "var(--steel)" }}>Loading verification ledger...</div>;
  }
  if (error) {
    return <div style={{ padding: 24, color: "var(--stamp)" }}>Error loading ledger: {error}</div>;
  }

  const ledgerRows = summary?.ledger || [];

  return (
    <div style={{ padding: "24px 32px", overflowY: "auto", height: "100vh" }}>
      <div style={{ marginBottom: 20 }}>
        <h1>Verification Desk Dashboard</h1>
        <div style={{ fontSize: 13, color: "var(--steel)", marginTop: 4 }}>
          Throughput and audit metrics across active recruitment vacancies
        </div>
      </div>

      {/* Top Ledger Table */}
      <div
        style={{
          backgroundColor: "var(--sheet)",
          borderRadius: "var(--radius-panel)",
          border: "var(--border-sheet)",
          padding: 20,
          marginBottom: 24,
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 14 }}>
          <h2>Primary verification ledger</h2>
          <div
            style={{ fontSize: 13, color: "var(--steel)", cursor: "help" }}
            title={`Hours saved formula: auto_verified (${summary?.processed || 0}) × ${summary?.manual_minutes_per_doc || 4} min / 60`}
          >
            <strong>{summary?.hours_saved || 0} hours saved</strong> (hover for formula)
          </div>
        </div>

        <table>
          <thead>
            <tr>
              <th>Document type</th>
              <th style={{ textAlign: "right" }}>Processed</th>
              <th style={{ textAlign: "right" }}>Auto-verified</th>
              <th style={{ textAlign: "right" }}>Sent to review</th>
              <th style={{ textAlign: "right" }}>Mismatches</th>
              <th style={{ textAlign: "right" }}>Time / doc</th>
            </tr>
          </thead>
          <tbody>
            {ledgerRows.length === 0 ? (
              <tr>
                <td colSpan={6} style={{ textAlign: "center", color: "var(--steel)", padding: 24 }}>
                  No documents processed yet. Run an instant check or start a batch to populate the ledger.
                </td>
              </tr>
            ) : (
              ledgerRows.map((row: any) => (
                <tr key={row.document_type}>
                  <td style={{ fontWeight: 600 }}>{row.document_type.replace(/_/g, " ")}</td>
                  <td style={{ textAlign: "right" }}>{row.processed}</td>
                  <td style={{ textAlign: "right", color: "var(--verified)", fontWeight: 600 }}>{row.auto_verified}</td>
                  <td style={{ textAlign: "right", color: "var(--caution)", fontWeight: 600 }}>{row.sent_to_review}</td>
                  <td style={{ textAlign: "right", color: "var(--stamp)", fontWeight: 600 }}>{row.mismatches}</td>
                  <td style={{ textAlign: "right" }}>{row.avg_ms} ms</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Two Analytical Breakdown Panels */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, marginBottom: 30 }}>
        {/* Chart 1: Where do mismatches come from? */}
        <div
          style={{
            backgroundColor: "var(--sheet)",
            borderRadius: "var(--radius-panel)",
            border: "var(--border-sheet)",
            padding: 20,
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 12 }}>
            <h3>Where do mismatches come from?</h3>
            <button
              onClick={() => onNavigate("applications")}
              style={{ background: "none", border: "none", color: "var(--ink)", fontSize: 12, textDecoration: "underline" }}
            >
              View applications
            </button>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {mismatches.length === 0 ? (
              <div style={{ fontSize: 13, color: "var(--steel)", padding: "16px 0" }}>No mismatches detected in recent runs.</div>
            ) : (
              mismatches.slice(0, 5).map((m: any, idx: number) => (
                <div key={idx} style={{ fontSize: 13 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
                    <span style={{ fontWeight: 600 }}>{m.field_name.replace(/_/g, " ")}</span>
                    <span style={{ color: "var(--stamp)", fontWeight: 600 }}>{m.count} cases</span>
                  </div>
                  <div style={{ fontSize: 12, color: "var(--steel)" }}>{m.reason}</div>
                  <div style={{ height: 4, backgroundColor: "#EAEFF2", borderRadius: 2, marginTop: 4 }}>
                    <div style={{ width: `${Math.min(100, m.count * 10)}%`, height: "100%", backgroundColor: "var(--stamp)" }} />
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Chart 2: Three Sigma and Review Rate */}
        <div
          style={{
            backgroundColor: "var(--sheet)",
            borderRadius: "var(--radius-panel)",
            border: "var(--border-sheet)",
            padding: 20,
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 12 }}>
            <h3>Field accuracy and human review rate</h3>
            <button
              onClick={() => onNavigate("review-queue")}
              style={{ background: "none", border: "none", color: "var(--ink)", fontSize: 12, textDecoration: "underline" }}
            >
              Open review queue
            </button>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {accuracy.length === 0 ? (
              <div style={{ fontSize: 13, color: "var(--steel)", padding: "16px 0" }}>
                Accuracy metrics will appear after human reviewers audit extracted fields.
              </div>
            ) : (
              accuracy.slice(0, 5).map((a: any, idx: number) => (
                <div key={idx} style={{ fontSize: 13 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
                    <span style={{ fontWeight: 600 }}>{a.field_name.replace(/_/g, " ")}</span>
                    <span>
                      <strong style={{ color: "var(--verified)" }}>{a.accuracy}% accuracy</strong> ({a.sample_size} samples)
                    </span>
                  </div>
                  <div style={{ fontSize: 12, color: "var(--steel)" }}>Review routing rate: {a.review_rate}%</div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
