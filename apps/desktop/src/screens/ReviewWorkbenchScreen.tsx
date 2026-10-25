// For: Interactive review workbench with document margin notes and leader lines
// Must never: Commit field corrections without persisting active reviewer credentials

import React, { useState, useEffect, useCallback } from "react";
import { advsApi } from "../services/api-client";
import { ArrowLeft } from "lucide-react";

interface WorkbenchProps {
  itemId: string;
  onBack: () => void;
}

export const ReviewWorkbenchScreen: React.FC<WorkbenchProps> = ({ itemId, onBack }) => {
  const [data, setData] = useState<any | null>(null);
  const [activeFieldIndex, setActiveFieldIndex] = useState<number>(0);
  const [editingValue, setEditingValue] = useState<string>("");
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [comment, setComment] = useState<string>("");

  const loadItem = async () => {
    try {
      const res = await advsApi.getReviewItemDetail(itemId);
      setData(res);
      if (res.fields && res.fields.length > 0) {
        setEditingValue(res.fields[0].extracted_value || "");
      }
    } catch {
      // Handled silently
    }
  };

  useEffect(() => {
    loadItem();
  }, [itemId]);

  const activeField = data?.fields?.[activeFieldIndex] || null;

  const handleDecision = useCallback(
    async (decision: "accepted" | "corrected" | "rejected") => {
      if (!activeField) return;
      const val = decision === "corrected" ? editingValue : undefined;
      await advsApi.submitFieldReview(activeField.id, { decision, corrected_value: val, comment });
      setIsEditing(false);
      setComment("");
      loadItem();
      // Move to next field
      if (data && activeFieldIndex < data.fields.length - 1) {
        setActiveFieldIndex((prev) => prev + 1);
      }
    },
    [activeField, editingValue, comment, data, activeFieldIndex]
  );

  const handleNextField = useCallback(() => {
    if (data && activeFieldIndex < data.fields.length - 1) {
      setActiveFieldIndex((prev) => prev + 1);
    } else {
      setActiveFieldIndex(0);
    }
  }, [data, activeFieldIndex]);

  // Keyboard navigation shortcuts: A, E, R, N
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (isEditing) return;
      if (e.key === "a" || e.key === "A") handleDecision("accepted");
      if (e.key === "e" || e.key === "E") setIsEditing(true);
      if (e.key === "r" || e.key === "R") handleDecision("rejected");
      if (e.key === "n" || e.key === "N") handleNextField();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handleDecision, handleNextField, isEditing]);

  const handleCompleteItem = async () => {
    await advsApi.completeReviewItem(itemId);
    onBack();
  };

  if (!data) {
    return <div style={{ padding: 32, color: "var(--steel)" }}>Opening review workbench...</div>;
  }


  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh", backgroundColor: "var(--desk)" }}>
      {/* Top Workbench Bar */}
      <div
        style={{
          padding: "12px 24px",
          backgroundColor: "var(--sheet)",
          borderBottom: "var(--border-subtle)",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <button onClick={onBack} style={{ display: "flex", alignItems: "center", gap: 4, background: "none", border: "none", color: "var(--steel)" }}>
            <ArrowLeft size={16} />
            <span>Queue</span>
          </button>
          <div style={{ height: 18, width: 1, backgroundColor: "var(--steel)" }} />
          <div>
            <span style={{ fontFamily: "var(--font-serif)", fontWeight: 700, fontSize: 16 }}>{data.application.full_name}</span>
            <span style={{ fontSize: 12, color: "var(--steel)", marginLeft: 8 }}>({data.application.registration_no})</span>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{ fontSize: 11, color: "var(--steel)", display: "flex", gap: 8 }}>
            <span><code>A</code> Accept</span>
            <span><code>E</code> Edit</span>
            <span><code>R</code> Reject</span>
            <span><code>N</code> Next</span>
          </div>
          <button
            onClick={handleCompleteItem}
            style={{ padding: "6px 14px", backgroundColor: "var(--verified)", color: "#FFF", border: "none", borderRadius: "var(--radius-input)", fontWeight: 600 }}
          >
            Complete review
          </button>
        </div>
      </div>

      {/* Main Inspection Desk Layout */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 380px", flex: 1, overflow: "hidden" }}>
        {/* Center: Document on Table Surface with Leader Lines & Bounding Boxes */}
        <div
          style={{
            padding: 24,
            overflowY: "auto",
            display: "flex",
            justifyContent: "center",
            alignItems: "flex-start",
            backgroundColor: "#DFE5E1",
          }}
        >
          <div
            style={{
              position: "relative",
              width: 720,
              minHeight: 900,
              backgroundColor: "#FFF",
              boxShadow: "0 4px 16px rgba(23, 40, 63, 0.12)",
              padding: 40,
              fontFamily: "var(--font-serif)",
            }}
          >
            <div style={{ textAlign: "center", borderBottom: "2px solid #17283F", paddingBottom: 16, marginBottom: 24 }}>
              <div style={{ fontSize: 18, fontWeight: 700 }}>RECRUITMENT & ASSESSMENT CENTRE</div>
              <div style={{ fontSize: 12, color: "var(--steel)" }}>{data.document.original_filename}</div>
            </div>

            {/* Simulated rendered document text representation */}
            <div style={{ fontSize: 14, lineHeight: 2 }}>
              <div>Candidate: <strong>{data.application.full_name}</strong></div>
              <div>Father: {data.application.father_name || "Mohan Sharma"}</div>
              <div>Date of birth: {data.application.dob || "14/05/1999"}</div>
              <div>Qualification: B.Tech (Electronics & Communication)</div>
              <div>Aggregate Percentage: <strong>72.40%</strong></div>
              <div>Roll No: EC21S12345</div>
            </div>

            {/* Bounding box highlight for currently active field */}
            {activeField && (
              <div
                style={{
                  position: "absolute",
                  left: 36,
                  top: 130 + activeFieldIndex * 36,
                  width: 320,
                  height: 32,
                  border: "2px solid var(--ink)",
                  backgroundColor: "rgba(23, 40, 63, 0.08)",
                  pointerEvents: "none",
                }}
              >
                <div
                  style={{
                    position: "absolute",
                    right: -24,
                    top: "50%",
                    width: 24,
                    height: 1,
                    backgroundColor: "var(--ink)",
                  }}
                />
              </div>
            )}
          </div>
        </div>

        {/* Right Margin Notes Column */}
        <div
          style={{
            backgroundColor: "var(--sheet)",
            borderLeft: "var(--border-subtle)",
            overflowY: "auto",
            padding: 20,
            display: "flex",
            flexDirection: "column",
            gap: 14,
          }}
        >
          <div style={{ fontSize: 12, fontWeight: 700, color: "var(--steel)", textTransform: "uppercase" }}>
            Extracted margin notes ({data.fields.length} fields)
          </div>

          {data.fields.map((f: any, idx: number) => {
            const isSelected = idx === activeFieldIndex;
            const statusClass = f.status === "match" ? "match" : f.status === "mismatch" ? "mismatch" : "caution";
            return (
              <div
                key={f.id}
                onClick={() => {
                  setActiveFieldIndex(idx);
                  setEditingValue(f.extracted_value || "");
                  setIsEditing(false);
                }}
                style={{
                  padding: 12,
                  borderRadius: "var(--radius-panel)",
                  border: isSelected ? "2px solid var(--ink)" : "var(--border-subtle)",
                  backgroundColor: isSelected ? "#FFF" : "var(--sheet)",
                  cursor: "pointer",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 4 }}>
                  <strong style={{ fontSize: 13 }}>{f.field_name.replace(/_/g, " ")}</strong>
                  <span className={`status-stamp ${statusClass}`}>{f.status}</span>
                </div>
                <div style={{ fontSize: 13, marginBottom: 2 }}>
                  Extracted: <strong style={{ color: "var(--ink)" }}>{f.extracted_value || "—"}</strong>
                </div>
                <div style={{ fontSize: 12, color: "var(--steel)" }}>Expected form value: {f.expected_value || "—"}</div>

                {/* Expanded Action Panel for Selected Field */}
                {isSelected && (
                  <div style={{ marginTop: 10, paddingTop: 10, borderTop: "1px solid #D5DCD8" }}>
                    {isEditing ? (
                      <div>
                        <input
                          type="text"
                          value={editingValue}
                          onChange={(e) => setEditingValue(e.target.value)}
                          style={{ width: "100%", padding: "6px 8px", border: "1px solid var(--steel)", marginBottom: 8 }}
                        />
                        <button
                          onClick={() => handleDecision("corrected")}
                          style={{ width: "100%", padding: "6px", backgroundColor: "var(--ink)", color: "#FFF", border: "none" }}
                        >
                          Save correction
                        </button>
                      </div>
                    ) : (
                      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 6 }}>
                        <button
                          onClick={() => handleDecision("accepted")}
                          style={{ padding: "6px", border: "1px solid var(--verified)", color: "var(--verified)", background: "#FFF" }}
                        >
                          Accept
                        </button>
                        <button
                          onClick={() => setIsEditing(true)}
                          style={{ padding: "6px", border: "1px solid var(--steel)", color: "var(--ink)", background: "#FFF" }}
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDecision("rejected")}
                          style={{ padding: "6px", border: "1px solid var(--stamp)", color: "var(--stamp)", background: "#FFF" }}
                        >
                          Reject
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
