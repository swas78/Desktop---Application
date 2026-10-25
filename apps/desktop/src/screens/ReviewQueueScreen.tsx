// For: Manual human review queue dispatching and workload claiming
// Must never: Reassign claimed review cases without officer confirmation

import React, { useState, useEffect } from "react";
import { advsApi } from "../services/api-client";


interface ReviewQueueProps {
  onOpenWorkbench: (itemId: string) => void;
}

export const ReviewQueueScreen: React.FC<ReviewQueueProps> = ({ onOpenWorkbench }) => {
  const [items, setItems] = useState<any[]>([]);
  const [statusFilter, setStatusFilter] = useState("open");
  const [isLoading, setIsLoading] = useState(true);

  const loadQueue = async () => {
    setIsLoading(true);
    try {
      const data = await advsApi.getReviewQueue(statusFilter);
      setItems(data);
    } catch {
      // Handled silently
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadQueue();
  }, [statusFilter]);

  const handleClaim = async (itemId: string) => {
    try {
      await advsApi.claimReviewItem(itemId);
      onOpenWorkbench(itemId);
    } catch (err: any) {
      alert(`Claim failed: ${err.message}`);
    }
  };

  return (
    <div style={{ padding: "24px 32px", overflowY: "auto", height: "100vh" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 20 }}>
        <div>
          <h1>Human Review Queue</h1>
          <div style={{ fontSize: 13, color: "var(--steel)", marginTop: 4 }}>
            Cases routed for manual inspection due to low confidence or biodata discrepancies
          </div>
        </div>

        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          style={{ padding: "8px 12px", border: "1px solid var(--steel)", borderRadius: "var(--radius-input)", backgroundColor: "var(--sheet)" }}
        >
          <option value="open">Open items</option>
          <option value="claimed">Claimed by me</option>
          <option value="completed">Completed</option>
        </select>
      </div>

      <div style={{ backgroundColor: "var(--sheet)", borderRadius: "var(--radius-panel)", border: "var(--border-sheet)" }}>
        <table>
          <thead>
            <tr>
              <th>Registration No</th>
              <th>Candidate Name</th>
              <th>Document</th>
              <th>Flag Reason</th>
              <th>Priority</th>
              <th>Queue Status</th>
              <th style={{ textAlign: "right" }}>Action</th>
            </tr>
          </thead>
          <tbody>
            {items.length === 0 ? (
              <tr>
                <td colSpan={7} style={{ textAlign: "center", color: "var(--steel)", padding: 32 }}>
                  {isLoading ? "Loading review queue..." : "No documents currently in review queue."}
                </td>
              </tr>
            ) : (
              items.map((item) => (
                <tr key={item.id}>
                  <td style={{ fontWeight: 600 }}>{item.registration_no}</td>
                  <td>{item.full_name}</td>
                  <td>{item.original_filename}</td>
                  <td>
                    <span className="status-stamp caution">{item.reason?.replace(/_/g, " ")}</span>
                  </td>
                  <td>
                    <span style={{ fontWeight: 600, color: item.priority > 0 ? "var(--stamp)" : "var(--steel)" }}>
                      {item.priority > 0 ? "High" : "Standard"}
                    </span>
                  </td>
                  <td style={{ textTransform: "capitalize" }}>{item.status}</td>
                  <td style={{ textAlign: "right" }}>
                    <button
                      onClick={() => handleClaim(item.id)}
                      style={{
                        padding: "6px 12px",
                        backgroundColor: "var(--ink)",
                        color: "#FFF",
                        border: "none",
                        borderRadius: "var(--radius-input)",
                        fontWeight: 600,
                        fontSize: 12,
                      }}
                    >
                      {item.status === "claimed" ? "Open workbench" : "Claim & Review"}
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
