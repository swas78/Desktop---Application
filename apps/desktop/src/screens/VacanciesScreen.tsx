// For: Recruitment vacancy configuration and eligibility rule authoring
// Must never: Delete active vacancy definitions that have submitted applications

import React, { useState, useEffect } from "react";
import { advsApi } from "../services/api-client";
import { Plus } from "lucide-react";

export const VacanciesScreen: React.FC = () => {
  const [vacancies, setVacancies] = useState<any[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [advtNo, setAdvtNo] = useState("RAC/2026/02");
  const [postName, setPostName] = useState("Scientist B (Computer Science)");
  const [closingDate, setClosingDate] = useState("2026-12-31");
  const [minPercentage, setMinPercentage] = useState(60);
  const [gateRequired, setGateRequired] = useState(true);
  const [testResult, setTestResult] = useState<string | null>(null);

  const loadVacancies = async () => {
    try {
      const data = await advsApi.getVacancies();
      setVacancies(data);
    } catch {
      // Handled silently
    }
  };

  useEffect(() => {
    loadVacancies();
  }, []);

  const handleCreateVacancy = async (e: React.FormEvent) => {
    e.preventDefault();
    const rules = {
      min_qualification: "BE/BTech",
      allowed_branches: ["CSE", "IT", "ECE"],
      min_percentage: Number(minPercentage),
      gate_required: gateRequired,
      gate_validity_years: 3,
      max_age: { UR: 28, OBC: 31, SC: 33, ST: 33, PwD_extra: 10 },
      required_documents: ["degree_marksheet", "gate_scorecard"],
    };
    try {
      await advsApi.createVacancy({
        advt_no: advtNo,
        post_name: postName,
        closing_date: closingDate,
        rules,
      });
      setShowModal(false);
      loadVacancies();
    } catch (err: any) {
      alert(`Error creating vacancy: ${err.message}`);
    }
  };

  const handleRunEligibilityBatch = async (id: string) => {
    try {
      const res = await advsApi.evaluateVacancyBatch(id);
      setTestResult(`Evaluated eligibility for ${res.evaluated} applications.`);
    } catch (err: any) {
      alert(`Error: ${err.message}`);
    }
  };

  return (
    <div style={{ padding: "24px 32px", overflowY: "auto", height: "100vh" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 20 }}>
        <div>
          <h1>Vacancies and Eligibility Rules</h1>
          <div style={{ fontSize: 13, color: "var(--steel)", marginTop: 4 }}>
            Define recruitment advertisements, qualification branches, and age relaxations
          </div>
        </div>

        <button
          onClick={() => setShowModal(true)}
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
          <Plus size={14} />
          <span>New vacancy</span>
        </button>
      </div>

      {testResult && (
        <div style={{ padding: 12, backgroundColor: "#E8F3EE", color: "var(--verified)", borderRadius: "var(--radius-input)", marginBottom: 16 }}>
          {testResult}
        </div>
      )}

      <div style={{ backgroundColor: "var(--sheet)", borderRadius: "var(--radius-panel)", border: "var(--border-sheet)" }}>
        <table>
          <thead>
            <tr>
              <th>Advertisement No</th>
              <th>Post Name</th>
              <th>Closing Date</th>
              <th>Min %</th>
              <th>GATE Required</th>
              <th>Status</th>
              <th style={{ textAlign: "right" }}>Eligibility Action</th>
            </tr>
          </thead>
          <tbody>
            {vacancies.length === 0 ? (
              <tr>
                <td colSpan={7} style={{ textAlign: "center", color: "var(--steel)", padding: 32 }}>
                  No vacancies defined. Click "New vacancy" to set up eligibility rules.
                </td>
              </tr>
            ) : (
              vacancies.map((v) => {
                const rules = typeof v.rules_json === "string" ? JSON.parse(v.rules_json) : v.rules_json;
                return (
                  <tr key={v.id}>
                    <td style={{ fontWeight: 600 }}>{v.advt_no}</td>
                    <td>{v.post_name}</td>
                    <td>{v.closing_date}</td>
                    <td>{rules?.min_percentage || 60}%</td>
                    <td>{rules?.gate_required ? "Yes" : "No"}</td>
                    <td>
                      <span className="status-stamp match">{v.status}</span>
                    </td>
                    <td style={{ textAlign: "right" }}>
                      <button
                        onClick={() => handleRunEligibilityBatch(v.id)}
                        style={{ padding: "4px 10px", border: "1px solid var(--steel)", background: "none", borderRadius: "var(--radius-input)" }}
                      >
                        Evaluate all
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div style={{ position: "fixed", top: 0, left: 0, right: 0, bottom: 0, backgroundColor: "rgba(23,40,63,0.4)", display: "flex", alignItems: "center", justifyContent: "center" }}>
          <div style={{ width: 440, backgroundColor: "var(--sheet)", padding: 24, borderRadius: "var(--radius-panel)" }}>
            <h3>Define New Vacancy Criteria</h3>
            <form onSubmit={handleCreateVacancy} style={{ marginTop: 16 }}>
              <div style={{ marginBottom: 10 }}>
                <label style={{ display: "block", fontSize: 12, color: "var(--steel)" }}>Advertisement No</label>
                <input type="text" value={advtNo} onChange={(e) => setAdvtNo(e.target.value)} required style={{ width: "100%", padding: 6 }} />
              </div>
              <div style={{ marginBottom: 10 }}>
                <label style={{ display: "block", fontSize: 12, color: "var(--steel)" }}>Post Name</label>
                <input type="text" value={postName} onChange={(e) => setPostName(e.target.value)} required style={{ width: "100%", padding: 6 }} />
              </div>
              <div style={{ marginBottom: 10 }}>
                <label style={{ display: "block", fontSize: 12, color: "var(--steel)" }}>Closing Date</label>
                <input type="date" value={closingDate} onChange={(e) => setClosingDate(e.target.value)} required style={{ width: "100%", padding: 6 }} />
              </div>
              <div style={{ marginBottom: 10 }}>
                <label style={{ display: "block", fontSize: 12, color: "var(--steel)" }}>Minimum Qualifying %</label>
                <input type="number" value={minPercentage} onChange={(e) => setMinPercentage(Number(e.target.value))} required style={{ width: "100%", padding: 6 }} />
              </div>
              <div style={{ marginBottom: 16 }}>
                <label style={{ fontSize: 13 }}>
                  <input type="checkbox" checked={gateRequired} onChange={(e) => setGateRequired(e.target.checked)} style={{ marginRight: 6 }} />
                  GATE scorecard mandatory
                </label>
              </div>
              <div style={{ display: "flex", justifyContent: "flex-end", gap: 10 }}>
                <button type="button" onClick={() => setShowModal(false)} style={{ padding: "6px 12px", background: "none", border: "1px solid var(--steel)" }}>
                  Cancel
                </button>
                <button type="submit" style={{ padding: "6px 14px", backgroundColor: "var(--ink)", color: "#FFF", border: "none" }}>
                  Save vacancy
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
