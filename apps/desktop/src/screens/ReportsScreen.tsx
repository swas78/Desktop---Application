// For: Official PDF and Excel verification report generation and export
// Must never: Embed unmasked applicant private cryptographic identifiers in exports

import React, { useState } from "react";
import { advsApi } from "../services/api-client";
import { Download } from "lucide-react";

export const ReportsScreen: React.FC = () => {
  const [reportType, setReportType] = useState("verification");
  const [format, setFormat] = useState<"pdf" | "xlsx">("pdf");
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedReport, setGeneratedReport] = useState<any | null>(null);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsGenerating(true);
    setGeneratedReport(null);
    try {
      const res = await advsApi.createReport({ type: reportType, format });
      setGeneratedReport(res);
    } catch (err: any) {
      alert(`Report error: ${err.message}`);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div style={{ padding: "24px 32px", overflowY: "auto", height: "100vh" }}>
      <div style={{ marginBottom: 20 }}>
        <h1>Verification Reports & Exports</h1>
        <div style={{ fontSize: 13, color: "var(--steel)", marginTop: 4 }}>
          Generate formal PDF audit dossiers and Excel spreadsheets for recruitment records
        </div>
      </div>

      <div style={{ maxWidth: 540, backgroundColor: "var(--sheet)", padding: 24, borderRadius: "var(--radius-panel)", border: "var(--border-sheet)" }}>
        <form onSubmit={handleGenerate}>
          <div style={{ marginBottom: 14 }}>
            <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "var(--steel)", marginBottom: 6 }}>
              Report Type
            </label>
            <select
              value={reportType}
              onChange={(e) => setReportType(e.target.value)}
              style={{ width: "100%", padding: "8px 10px", border: "1px solid var(--steel)", borderRadius: "var(--radius-input)", backgroundColor: "#FFF" }}
            >
              <option value="verification">Verification Outcome Dossier</option>
              <option value="shortlist">Eligible Candidate Shortlist</option>
            </select>
          </div>

          <div style={{ marginBottom: 20 }}>
            <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "var(--steel)", marginBottom: 6 }}>
              Export Format
            </label>
            <div style={{ display: "flex", gap: 16 }}>
              <label style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13 }}>
                <input
                  type="radio"
                  name="format"
                  checked={format === "pdf"}
                  onChange={() => setFormat("pdf")}
                />
                PDF Document (.pdf)
              </label>
              <label style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13 }}>
                <input
                  type="radio"
                  name="format"
                  checked={format === "xlsx"}
                  onChange={() => setFormat("xlsx")}
                />
                Excel Workbook (.xlsx)
              </label>
            </div>
          </div>

          <button
            type="submit"
            disabled={isGenerating}
            style={{
              padding: "10px 20px",
              backgroundColor: "var(--ink)",
              color: "#FFF",
              border: "none",
              borderRadius: "var(--radius-input)",
              fontWeight: 600,
              cursor: isGenerating ? "not-allowed" : "pointer",
            }}
          >
            {isGenerating ? "Generating report..." : "Generate report"}
          </button>
        </form>

        {generatedReport && (
          <div
            style={{
              marginTop: 20,
              padding: 16,
              backgroundColor: "#E8F3EE",
              border: "1px solid var(--verified)",
              borderRadius: "var(--radius-input)",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <div>
              <div style={{ fontWeight: 600, color: "var(--verified)", fontSize: 13 }}>Report Generated Successfully</div>
              <div style={{ fontSize: 12, color: "var(--ink)" }}>{generatedReport.filename}</div>
            </div>
            <a
              href={advsApi.getReportDownloadUrl(generatedReport.id)}
              download
              target="_blank"
              rel="noreferrer"
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 6,
                padding: "6px 12px",
                backgroundColor: "var(--verified)",
                color: "#FFF",
                borderRadius: "var(--radius-input)",
                textDecoration: "none",
                fontSize: 12,
                fontWeight: 600,
              }}
            >
              <Download size={14} />
              <span>Download</span>
            </a>
          </div>
        )}
      </div>
    </div>
  );
};
