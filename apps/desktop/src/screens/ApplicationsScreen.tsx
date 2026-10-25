// For: Candidate applications listing, status filtering, and 1-click batch screening
// Must never: Modify application records without writing to the audit log

import React, { useState, useEffect } from "react";
import { advsApi } from "../services/api-client";
import { Search, Upload, Play } from "lucide-react";

interface ApplicationsProps {
  onSelectApplication: (id: string) => void;
}

export const ApplicationsScreen: React.FC<ApplicationsProps> = ({ onSelectApplication }) => {
  const [applications, setApplications] = useState<any[]>([]);
  const [vacancies, setVacancies] = useState<any[]>([]);
  const [selectedVacancy, setSelectedVacancy] = useState<string>("");
  const [selectedStatus, setSelectedStatus] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [showImportModal, setShowImportModal] = useState(false);
  const [importJsonText, setImportJsonText] = useState("");
  const [notice, setNotice] = useState<string | null>(null);
  const [isBatchRunning, setIsBatchRunning] = useState(false);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [apps, vacs] = await Promise.all([
        advsApi.getApplications({
          vacancy_id: selectedVacancy || undefined,
          status: selectedStatus || undefined,
          search: searchQuery || undefined,
        }),
        advsApi.getVacancies(),
      ]);
      setApplications(apps);
      setVacancies(vacs);
    } catch {
      // Handled silently
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedVacancy, selectedStatus]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadData();
  };

  const handleImportSubmit = async () => {
    try {
      const parsed = JSON.parse(importJsonText);
      const rows = Array.isArray(parsed) ? parsed : [parsed];
      const res = await advsApi.importApplications({ rows, vacancy_id: selectedVacancy || (vacancies[0]?.id ?? "") });
      setNotice(`Successfully imported ${res.imported} applications.`);
      setShowImportModal(false);
      loadData();
    } catch (err: any) {
      setNotice(`Import error: ${err.message}`);
    }
  };

  const handleStartBatch = async () => {
    setIsBatchRunning(true);
    try {
      const res = await advsApi.createJob({
        scope: selectedVacancy ? "vacancy" : "all_pending",
        vacancy_id: selectedVacancy || undefined,
        mode: "quick",
      });
      setNotice(`Batch screening job launched (${res.total} documents in queue).`);
      setTimeout(loadData, 1000);
    } catch (err: any) {
      setNotice(`Batch launch error: ${err.message}`);
    } finally {
      setIsBatchRunning(false);
    }
  };

  return (
    <div style={{ padding: "24px 32px", overflowY: "auto", height: "100vh" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 20 }}>
        <div>
          <h1>Applications & Screening</h1>
          <div style={{ fontSize: 13, color: "var(--steel)", marginTop: 4 }}>
            Applicant registry, supporting documents, and 1-click batch verification
          </div>
        </div>

        <div style={{ display: "flex", gap: 10 }}>
          <button
            onClick={handleStartBatch}
            disabled={isBatchRunning}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 6,
              padding: "8px 14px",
              backgroundColor: "var(--verified)",
              color: "#FFF",
              border: "none",
              borderRadius: "var(--radius-input)",
              fontWeight: 600,
            }}
          >
            <Play size={14} />
            <span>{isBatchRunning ? "Starting batch..." : "Run batch screening"}</span>
          </button>
          <button
            onClick={() => setShowImportModal(true)}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 6,
              padding: "8px 14px",
              backgroundColor: "var(--ink)",
              color: "#FFF",
              border: "none",
              borderRadius: "var(--radius-input)",
              fontWeight: 600,
            }}
          >
            <Upload size={14} />
            <span>Import biodata</span>
          </button>
        </div>
      </div>

      {notice && (
        <div style={{ padding: 10, backgroundColor: "#E8F3EE", color: "var(--verified)", borderRadius: "var(--radius-input)", marginBottom: 16 }}>
          {notice}
        </div>
      )}

      {/* Filter toolbar */}
      <div style={{ display: "flex", gap: 12, marginBottom: 16 }}>
        <form onSubmit={handleSearchSubmit} style={{ display: "flex", flex: 1, gap: 8 }}>
          <div style={{ position: "relative", flex: 1 }}>
            <Search size={15} style={{ position: "absolute", left: 10, top: 10, color: "var(--steel)" }} />
            <input
              type="text"
              placeholder="Search by registration number or candidate name..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                width: "100%",
                padding: "8px 10px 8px 32px",
                border: "1px solid var(--steel)",
                borderRadius: "var(--radius-input)",
                backgroundColor: "var(--sheet)",
              }}
            />
          </div>
          <button type="submit" style={{ padding: "8px 14px", border: "1px solid var(--steel)", backgroundColor: "var(--sheet)" }}>
            Search
          </button>
        </form>

        <select
          value={selectedVacancy}
          onChange={(e) => setSelectedVacancy(e.target.value)}
          style={{ padding: "8px 12px", border: "1px solid var(--steel)", borderRadius: "var(--radius-input)", backgroundColor: "var(--sheet)" }}
        >
          <option value="">All vacancies</option>
          {vacancies.map((v) => (
            <option key={v.id} value={v.id}>
              {v.post_name} ({v.advt_no})
            </option>
          ))}
        </select>

        <select
          value={selectedStatus}
          onChange={(e) => setSelectedStatus(e.target.value)}
          style={{ padding: "8px 12px", border: "1px solid var(--steel)", borderRadius: "var(--radius-input)", backgroundColor: "var(--sheet)" }}
        >
          <option value="">All statuses</option>
          <option value="pending">Pending</option>
          <option value="processing">Processing</option>
          <option value="verified">Verified</option>
          <option value="needs_review">Needs Review</option>
          <option value="rejected">Rejected</option>
        </select>
      </div>

      {/* Applications Table */}
      <div style={{ backgroundColor: "var(--sheet)", borderRadius: "var(--radius-panel)", border: "var(--border-sheet)" }}>
        <table>
          <thead>
            <tr>
              <th>Registration No</th>
              <th>Full Name</th>
              <th>Date of Birth</th>
              <th>Category</th>
              <th>Verification Status</th>
              <th>Eligibility</th>
              <th style={{ textAlign: "right" }}>Inspect</th>
            </tr>
          </thead>
          <tbody>
            {applications.length === 0 ? (
              <tr>
                <td colSpan={7} style={{ textAlign: "center", color: "var(--steel)", padding: 32 }}>
                  {isLoading ? "Loading records..." : "No applications found. Import a file or run batch screening."}
                </td>
              </tr>
            ) : (
              applications.map((app) => (
                <tr key={app.id} style={{ cursor: "pointer" }} onClick={() => onSelectApplication(app.id)}>
                  <td style={{ fontWeight: 600 }}>{app.registration_no}</td>
                  <td>{app.full_name}</td>
                  <td>{app.dob || "—"}</td>
                  <td>{app.category || "UR"}</td>
                  <td>
                    <span className={`status-stamp ${app.status === "verified" ? "match" : app.status === "needs_review" ? "caution" : "not_found"}`}>
                      {app.status.replace(/_/g, " ")}
                    </span>
                  </td>
                  <td>
                    <span style={{ fontWeight: 600, color: app.eligibility === "eligible" ? "var(--verified)" : app.eligibility === "not_eligible" ? "var(--stamp)" : "var(--steel)" }}>
                      {app.eligibility.replace(/_/g, " ")}
                    </span>
                  </td>
                  <td style={{ textAlign: "right" }}>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectApplication(app.id);
                      }}
                      style={{ padding: "4px 8px", background: "none", border: "1px solid var(--steel)", borderRadius: "var(--radius-input)" }}
                    >
                      Inspect
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Import Modal */}
      {showImportModal && (
        <div style={{ position: "fixed", top: 0, left: 0, right: 0, bottom: 0, backgroundColor: "rgba(23, 40, 63, 0.4)", display: "flex", alignItems: "center", justifyContent: "center" }}>
          <div style={{ width: 480, backgroundColor: "var(--sheet)", padding: 24, borderRadius: "var(--radius-panel)", border: "var(--border-sheet)" }}>
            <h3>Import Application Records (JSON)</h3>
            <textarea
              rows={8}
              value={importJsonText}
              onChange={(e) => setImportJsonText(e.target.value)}
              placeholder='[{"registration_no": "RAC240001", "fullName": "A. Kumar", "dob": "1999-05-14", "qualification": {"branch": "ECE", "percentage": 74.2}}]'
              style={{ width: "100%", padding: 8, fontFamily: "monospace", fontSize: 12, border: "1px solid var(--steel)", borderRadius: "var(--radius-input)", marginTop: 10, marginBottom: 14 }}
            />
            <div style={{ display: "flex", justifyContent: "flex-end", gap: 10 }}>
              <button onClick={() => setShowImportModal(false)} style={{ padding: "6px 12px", border: "1px solid var(--steel)", background: "transparent" }}>
                Cancel
              </button>
              <button onClick={handleImportSubmit} style={{ padding: "6px 14px", backgroundColor: "var(--ink)", color: "#FFF", border: "none" }}>
                Import records
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
