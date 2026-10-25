// For: Permanent left navigation rail reflecting streamlined 4-desk workflow
// Must never: Execute destructive data mutations or hide role checks client-side

import React from "react";
import { Zap, CheckSquare, Users, Shield, LogOut } from "lucide-react";

interface SidebarProps {
  currentScreen: string;
  onNavigate: (screen: string) => void;
  userRole: string;
  onLogout: () => void;
  userName: string;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentScreen,
  onNavigate,
  userRole,
  onLogout,
  userName,
}) => {
  const navItems = [
    { id: "verification-desk", label: "Verification Desk", icon: Zap, roles: ["admin", "officer"] },
    { id: "review-workbench", label: "Review Workbench", icon: CheckSquare, roles: ["admin", "officer", "reviewer"] },
    { id: "applications", label: "Applications & Batch", icon: Users, roles: ["admin", "officer", "reviewer"] },
    { id: "ledger-admin", label: "Ledger & Admin", icon: Shield, roles: ["admin", "officer", "reviewer"] },
  ];

  const filteredItems = navItems.filter((item) => item.roles.includes(userRole));

  return (
    <aside
      style={{
        width: 240,
        backgroundColor: "var(--sheet)",
        borderRight: "var(--border-subtle)",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        height: "100vh",
        userSelect: "none",
      }}
    >
      <div>
        <div style={{ padding: "24px 18px", borderBottom: "1px solid #E8ECEA" }}>
          <div className="editorial-hero" style={{ fontSize: 22, color: "var(--ink)", marginBottom: 2 }}>
            RAC ADVS
          </div>
          <div style={{ fontSize: 11, color: "var(--steel)", textTransform: "uppercase", letterSpacing: 0.6, fontWeight: 600 }}>
            DRDO Screening Suite
          </div>
          <div style={{ marginTop: 10 }}>
            <span className="badge-lock" style={{ fontSize: 10, padding: "2px 8px" }}>🔒 Air-Gapped</span>
          </div>
        </div>

        <nav style={{ padding: "16px 10px" }}>
          {filteredItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentScreen === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                  width: "100%",
                  padding: "10px 14px",
                  marginBottom: 6,
                  border: "none",
                  backgroundColor: isActive ? "var(--ink)" : "transparent",
                  color: isActive ? "#FFFFFF" : "var(--ink)",
                  fontWeight: isActive ? 600 : 500,
                  borderRadius: "9999px",
                  textAlign: "left",
                  fontSize: 13,
                  transition: "all 0.15s ease",
                }}
              >
                <Icon size={16} strokeWidth={isActive ? 2.4 : 1.8} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      <div style={{ padding: "18px 16px", borderTop: "1px solid #E8ECEA", backgroundColor: "var(--sheet)" }}>
        <div style={{ fontSize: 13, fontWeight: 700, color: "var(--ink)", marginBottom: 2 }}>{userName}</div>
        <div style={{ fontSize: 11, color: "var(--steel)", textTransform: "capitalize", marginBottom: 12 }}>
          Role: {userRole}
        </div>
        <button
          onClick={onLogout}
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            width: "100%",
            padding: "8px 12px",
            border: "1px solid #C4CEC8",
            backgroundColor: "#FFF",
            color: "var(--ink)",
            borderRadius: "9999px",
            justifyContent: "center",
            fontWeight: 600,
            fontSize: 12,
          }}
        >
          <LogOut size={13} />
          <span>Sign out</span>
        </button>
      </div>
    </aside>
  );
};
