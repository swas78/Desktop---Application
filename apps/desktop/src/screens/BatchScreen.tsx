// For: Batch verification job creation and live queue supervision
// Must never: Block UI rendering during long-running batch executions

import React, { useState, useEffect } from "react";
import { advsApi } from "../services/api-client";
import { Play, Pause, XOctagon } from "lucide-react";

export const BatchScreen: React.FC = () => {
  const [jobs, setJobs] = useState<any[]>([]);
  const [vacancies, setVacancies] = useState<any[]>([]);
  const [selectedVacancy, setSelectedVacancy] = useState<string>("");
  const [mode, setMode] = useState<"quick" | "deep">("quick");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const loadData = async () => {
    try {
      const [jList, vList] = await Promise.all([advsApi.getJobs(), advsApi.getVacancies()]);
      setJobs(jList);
      setVacancies(vList);
    } catch {
      // Handled silently
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 2000);
    return () => clearInterval(interval);
  }, []);

  const handleStartBatch = async () => {
    setIsSubmitting(true);
    try {
      await advsApi.createJob({
        scope: selectedVacancy ? "vacancy" : "all_pending",
        vacancy_id: selectedVacancy || undefined,
        mode,
      });
      loadData();
    } catch (err: any) {
      alert(`Batch error: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handlePause = async (id: string) => {
    await advsApi.pauseJob(id);
    loadData();
  };

  const handleResume = async (id: string) => {
    await advsApi.resumeJob(id);
    loadData();
  };

  const handleCancel = async (id: string) => {
    await advsApi.cancelJob(id);
    loadData();
  };

  return (
    <div style={{ padding: "24px 32px", overflowY: "auto", height: "100vh" }}>
      <div style={{ marginBottom: 20 }}>
        <h1>Batch Screening Verification</h1>
        <div style={{ fontSize: 13, color: "var(--steel)", marginTop: 4 }}>
          Run high-throughput document verification across queued candidate applications
        </div>
      </div>

      {/* Control Configuration Panel */}
      <div
        style={{
          backgroundColor: "var(--sheet)",
          padding: 20,
          borderRadius: "var(--radius-panel)",
          border: "var(--border-sheet)",
          marginBottom: 24,
          display: "flex",
          gap: 16,
          alignItems: "flex-end",
        }}
      >
        <div style={{ flex: 1 }}>
          <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "var(--steel)", marginBottom: 4 }}>
            Vacancy scope
          </label>
          <select
            value={selectedVacancy}
            onChange={(e) => setSelectedVacancy(e.target.value)}
            style={{ width: "100%", padding: "8px 10px", border: "1px solid var(--steel)", borderRadius: "var(--radius-input)", backgroundColor: "#FFF" }}
          >
            <option value="">All pending uploaded applications</option>
            {vacancies.map((v) => (
              <option key={v.id} value={v.id}>
                {v.post_name} ({v.advt_no})
              </option>
            ))}
          </select>
        </div>

        <div style={{ width: 180 }}>
          <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "var(--steel)", marginBottom: 4 }}>
            Extraction mode
          </label>
          <select
            value={mode}
            onChange={(e) => setMode(e.target.value as any)}
            style={{ width: "100%", padding: "8px 10px", border: "1px solid var(--steel)", borderRadius: "var(--radius-input)", backgroundColor: "#FFF" }}
          >
            <option value="quick">Quick (Standard)</option>
            <option value="deep">Deep (Comprehensive)</option>
          </select>
        </div>

        <button
          onClick={handleStartBatch}
          disabled={isSubmitting}
          style={{
            padding: "9px 20px",
            backgroundColor: "var(--ink)",
            color: "#FFF",
            border: "none",
            borderRadius: "var(--radius-input)",
            fontWeight: 600,
            cursor: isSubmitting ? "not-allowed" : "pointer",
          }}
        >
          {isSubmitting ? "Starting..." : "Start batch"}
        </button>
      </div>

      {/* Active and Past Jobs Ledger */}
      <div style={{ backgroundColor: "var(--sheet)", borderRadius: "var(--radius-panel)", border: "var(--border-sheet)" }}>
        <table>
          <thead>
            <tr>
              <th>Job ID</th>
              <th>Mode</th>
              <th>Progress</th>
              <th>Status</th>
              <th>Created at</th>
              <th style={{ textAlign: "right" }}>Controls</th>
            </tr>
          </thead>
          <tbody>
            {jobs.length === 0 ? (
              <tr>
                <td colSpan={6} style={{ textAlign: "center", color: "var(--steel)", padding: 32 }}>
                  No batch screening jobs launched yet.
                </td>
              </tr>
            ) : (
              jobs.map((job) => {
                const pct = job.total > 0 ? Math.round((job.done / job.total) * 100) : 100;
                return (
                  <tr key={job.id}>
                    <td style={{ fontWeight: 600, fontFamily: "monospace" }}>{job.id.substring(0, 8)}...</td>
                    <td style={{ textTransform: "capitalize" }}>{job.mode}</td>
                    <td style={{ width: 220 }}>
                      <div style={{ fontSize: 12, marginBottom: 4 }}>
                        {job.done} / {job.total} completed ({pct}%)
                      </div>
                      <div style={{ height: 6, width: "100%", backgroundColor: "#D9E1DC", borderRadius: 3, overflow: "hidden" }}>
                        <div style={{ width: `${pct}%`, height: "100%", backgroundColor: "var(--ink)" }} />
                      </div>
                    </td>
                    <td>
                      <span className={`status-stamp ${job.state === "completed" ? "match" : job.state === "running" ? "caution" : "not_found"}`}>
                        {job.state}
                      </span>
                    </td>
                    <td>{new Date(job.created_at).toLocaleTimeString()}</td>
                    <td style={{ textAlign: "right" }}>
                      {job.state === "running" && (
                        <button onClick={() => handlePause(job.id)} style={{ padding: "4px 8px", marginRight: 6, border: "1px solid var(--steel)", background: "none" }}>
                          <Pause size={12} />
                        </button>
                      )}
                      {job.state === "paused" && (
                        <button onClick={() => handleResume(job.id)} style={{ padding: "4px 8px", marginRight: 6, border: "1px solid var(--steel)", background: "none" }}>
                          <Play size={12} />
                        </button>
                      )}
                      {(job.state === "running" || job.state === "paused") && (
                        <button onClick={() => handleCancel(job.id)} style={{ padding: "4px 8px", border: "1px solid var(--stamp)", color: "var(--stamp)", background: "none" }}>
                          <XOctagon size={12} />
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
