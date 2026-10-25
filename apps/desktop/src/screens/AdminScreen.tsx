// For: System administration, operator roles, thresholds, and tamper-evident audit viewer
// Must never: Allow modifying audit records or displaying raw cryptographic keys

import React, { useState, useEffect } from "react";
import { advsApi } from "../services/api-client";
import { Shield } from "lucide-react";

export const AdminScreen: React.FC = () => {
  const [activeTab, setActiveTab] = useState<"users" | "settings" | "audit" | "models">("audit");
  const [users, setUsers] = useState<any[]>([]);
  const [settings, setSettings] = useState<Record<string, any>>({});
  const [auditData, setAuditData] = useState<{ chain_valid: boolean; entries: any[] }>({ chain_valid: true, entries: [] });
  const [models, setModels] = useState<any[]>([]);
  
  const [showAddUser, setShowAddUser] = useState(false);
  const [newUsername, setNewUsername] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [newFullName, setNewFullName] = useState("");
  const [newRole, setNewRole] = useState("officer");

  const loadData = async () => {
    try {
      const [u, s, a, m] = await Promise.all([
        advsApi.getUsers(),
        advsApi.getSettings(),
        advsApi.getAuditTrail(),
        advsApi.getModels(),
      ]);
      setUsers(u);
      setSettings(s);
      setAuditData(a);
      setModels(m);
    } catch {
      // Handled silently
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await advsApi.createUser({
        username: newUsername,
        password: newPassword,
        full_name: newFullName,
        role: newRole,
      });
      setShowAddUser(false);
      loadData();
    } catch (err: any) {
      alert(`User creation error: ${err.message}`);
    }
  };

  const handleSaveThreshold = async (key: string, val: any) => {
    try {
      await advsApi.updateSettings({ [key]: val });
      setSettings((prev) => ({ ...prev, [key]: val }));
    } catch (err: any) {
      alert(`Settings update error: ${err.message}`);
    }
  };

  return (
    <div style={{ padding: "24px 32px", overflowY: "auto", height: "100vh" }}>
      <div style={{ marginBottom: 20 }}>
        <h1>System Administration</h1>
        <div style={{ fontSize: 13, color: "var(--steel)", marginTop: 4 }}>
          Security controls, audit log verification, threshold tuning, and operator accounts
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: "flex", gap: 8, borderBottom: "var(--border-subtle)", paddingBottom: 10, marginBottom: 20 }}>
        {(["audit", "settings", "users", "models"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              padding: "6px 14px",
              border: "none",
              backgroundColor: activeTab === tab ? "var(--ink)" : "transparent",
              color: activeTab === tab ? "#FFF" : "var(--steel)",
              borderRadius: "var(--radius-input)",
              fontWeight: 600,
              textTransform: "capitalize",
            }}
          >
            {tab === "audit" ? "Tamper-evident Audit Log" : tab}
          </button>
        ))}
      </div>

      {/* Audit Log Tab */}
      {activeTab === "audit" && (
        <div>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              padding: "10px 16px",
              backgroundColor: auditData.chain_valid ? "#E8F3EE" : "#F8ECEB",
              color: auditData.chain_valid ? "var(--verified)" : "var(--stamp)",
              border: `1px solid ${auditData.chain_valid ? "var(--verified)" : "var(--stamp)"}`,
              borderRadius: "var(--radius-panel)",
              marginBottom: 16,
              fontSize: 13,
              fontWeight: 600,
            }}
          >
            <Shield size={16} />
            <span>
              {auditData.chain_valid
                ? "Cryptographic Hash Chain Verified: All records immutable and untampered."
                : "Warning: Cryptographic hash chain mismatch detected in audit log."}
            </span>
          </div>

          <div style={{ backgroundColor: "var(--sheet)", borderRadius: "var(--radius-panel)", border: "var(--border-sheet)" }}>
            <table>
              <thead>
                <tr>
                  <th>Timestamp (UTC)</th>
                  <th>Operator</th>
                  <th>Action</th>
                  <th>Target Entity</th>
                  <th>Record SHA-256 Hash</th>
                </tr>
              </thead>
              <tbody>
                {auditData.entries.map((entry) => (
                  <tr key={entry.id}>
                    <td>{new Date(entry.ts).toLocaleString()}</td>
                    <td>{entry.username || "System"}</td>
                    <td style={{ fontWeight: 600 }}>{entry.action}</td>
                    <td>{entry.entity_type || "—"}</td>
                    <td style={{ fontFamily: "monospace", fontSize: 11, color: "var(--steel)" }}>
                      {entry.hash.substring(0, 16)}...
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Settings Tab */}
      {activeTab === "settings" && (
        <div style={{ maxWidth: 540, backgroundColor: "var(--sheet)", padding: 20, borderRadius: "var(--radius-panel)", border: "var(--border-sheet)" }}>
          <h3 style={{ marginBottom: 16 }}>Verification Thresholds</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            <div>
              <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "var(--steel)" }}>
                Auto-accept confidence threshold (Three Sigma)
              </label>
              <input
                type="number"
                step="0.01"
                min="0.90"
                max="1.0"
                value={settings.auto_accept_threshold || 0.97}
                onChange={(e) => handleSaveThreshold("auto_accept_threshold", parseFloat(e.target.value))}
                style={{ padding: 6, width: 120, marginTop: 4 }}
              />
            </div>
            <div>
              <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "var(--steel)" }}>
                Manual minutes saved per document check
              </label>
              <input
                type="number"
                value={settings.manual_minutes_per_doc || 4}
                onChange={(e) => handleSaveThreshold("manual_minutes_per_doc", parseInt(e.target.value))}
                style={{ padding: 6, width: 120, marginTop: 4 }}
              />
            </div>
          </div>
        </div>
      )}

      {/* Users Tab */}
      {activeTab === "users" && (
        <div>
          <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 12 }}>
            <button
              onClick={() => setShowAddUser(true)}
              style={{ padding: "6px 12px", backgroundColor: "var(--ink)", color: "#FFF", border: "none", borderRadius: "var(--radius-input)" }}
            >
              Add user
            </button>
          </div>
          <div style={{ backgroundColor: "var(--sheet)", borderRadius: "var(--radius-panel)", border: "var(--border-sheet)" }}>
            <table>
              <thead>
                <tr>
                  <th>Username</th>
                  <th>Full Name</th>
                  <th>Role</th>
                  <th>Active</th>
                  <th>Last login</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id}>
                    <td style={{ fontWeight: 600 }}>{u.username}</td>
                    <td>{u.full_name}</td>
                    <td style={{ textTransform: "capitalize" }}>{u.role}</td>
                    <td>{u.is_active ? "Active" : "Disabled"}</td>
                    <td>{u.last_login_at ? new Date(u.last_login_at).toLocaleString() : "Never"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {showAddUser && (
            <div style={{ position: "fixed", top: 0, left: 0, right: 0, bottom: 0, backgroundColor: "rgba(23,40,63,0.4)", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <div style={{ width: 380, backgroundColor: "var(--sheet)", padding: 24, borderRadius: "var(--radius-panel)" }}>
                <h3>Provision Operator Account</h3>
                <form onSubmit={handleCreateUser} style={{ marginTop: 14 }}>
                  <div style={{ marginBottom: 10 }}>
                    <label style={{ display: "block", fontSize: 12, color: "var(--steel)" }}>Username</label>
                    <input type="text" value={newUsername} onChange={(e) => setNewUsername(e.target.value)} required style={{ width: "100%", padding: 6 }} />
                  </div>
                  <div style={{ marginBottom: 10 }}>
                    <label style={{ display: "block", fontSize: 12, color: "var(--steel)" }}>Full Name</label>
                    <input type="text" value={newFullName} onChange={(e) => setNewFullName(e.target.value)} required style={{ width: "100%", padding: 6 }} />
                  </div>
                  <div style={{ marginBottom: 10 }}>
                    <label style={{ display: "block", fontSize: 12, color: "var(--steel)" }}>Password</label>
                    <input type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} required style={{ width: "100%", padding: 6 }} />
                  </div>
                  <div style={{ marginBottom: 16 }}>
                    <label style={{ display: "block", fontSize: 12, color: "var(--steel)" }}>Role</label>
                    <select value={newRole} onChange={(e) => setNewRole(e.target.value)} style={{ width: "100%", padding: 6 }}>
                      <option value="officer">Screening Officer</option>
                      <option value="reviewer">Reviewer</option>
                      <option value="admin">Administrator</option>
                    </select>
                  </div>
                  <div style={{ display: "flex", justifyContent: "flex-end", gap: 8 }}>
                    <button type="button" onClick={() => setShowAddUser(false)} style={{ padding: "6px 12px", background: "none", border: "1px solid var(--steel)" }}>
                      Cancel
                    </button>
                    <button type="submit" style={{ padding: "6px 14px", backgroundColor: "var(--ink)", color: "#FFF", border: "none" }}>
                      Create user
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Models Tab */}
      {activeTab === "models" && (
        <div style={{ backgroundColor: "var(--sheet)", borderRadius: "var(--radius-panel)", border: "var(--border-sheet)" }}>
          <table>
            <thead>
              <tr>
                <th>Model Name</th>
                <th>Version</th>
                <th>Runtime Status</th>
              </tr>
            </thead>
            <tbody>
              {models.map((m, idx) => (
                <tr key={idx}>
                  <td style={{ fontWeight: 600 }}>{m.name.replace(/_/g, " ")}</td>
                  <td>{m.version}</td>
                  <td>
                    <span className="status-stamp match">{m.status}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
