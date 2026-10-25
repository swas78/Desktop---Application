// For: Main application state router, navigation orchestrator, and screen coordinator
// Must never: Render administrative tools to unauthorized reviewer sessions

import React, { useState } from "react";
import { Sidebar } from "./components/Sidebar";
import { SplashScreen } from "./screens/SplashScreen";
import { LoginScreen } from "./screens/LoginScreen";
import { InstantCheckScreen } from "./screens/InstantCheckScreen";
import { ReviewQueueScreen } from "./screens/ReviewQueueScreen";
import { ReviewWorkbenchScreen } from "./screens/ReviewWorkbenchScreen";
import { ApplicationsScreen } from "./screens/ApplicationsScreen";
import { ApplicationDetailScreen } from "./screens/ApplicationDetailScreen";
import { LedgerAdminScreen } from "./screens/LedgerAdminScreen";
import { setAuthToken } from "./services/api-client";

export const App: React.FC = () => {
  const [currentScreen, setCurrentScreen] = useState<string>("splash");
  const [currentUser, setCurrentUser] = useState<any | null>(null);
  const [selectedAppId, setSelectedAppId] = useState<string | null>(null);
  const [selectedReviewItemId, setSelectedReviewItemId] = useState<string | null>(null);

  const handleSplashReady = () => {
    setCurrentScreen("login");
  };

  const handleLoginSuccess = (user: any) => {
    setCurrentUser(user);
    setCurrentScreen("verification-desk");
  };

  const handleLogout = () => {
    setAuthToken(null);
    setCurrentUser(null);
    setCurrentScreen("login");
  };

  const handleSelectApplication = (appId: string) => {
    setSelectedAppId(appId);
    setCurrentScreen("application-detail");
  };

  const handleOpenWorkbench = (itemId: string) => {
    setSelectedReviewItemId(itemId);
    setCurrentScreen("review-workbench");
  };

  if (currentScreen === "splash") {
    return <SplashScreen onReady={handleSplashReady} />;
  }

  if (currentScreen === "login" || !currentUser) {
    return <LoginScreen onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <div style={{ display: "flex", width: "100vw", height: "100vh", overflow: "hidden" }}>
      <Sidebar
        currentScreen={currentScreen}
        onNavigate={(screen) => {
          setSelectedReviewItemId(null);
          setCurrentScreen(screen);
        }}
        userRole={currentUser.role}
        onLogout={handleLogout}
        userName={currentUser.name}
      />
      <main style={{ flex: 1, backgroundColor: "var(--desk)", overflow: "hidden" }}>
        {currentScreen === "verification-desk" && (
          <InstantCheckScreen onOpenWorkbench={() => setCurrentScreen("review-workbench")} />
        )}
        {currentScreen === "review-workbench" && (
          selectedReviewItemId ? (
            <ReviewWorkbenchScreen
              itemId={selectedReviewItemId}
              onBack={() => setSelectedReviewItemId(null)}
            />
          ) : (
            <ReviewQueueScreen onOpenWorkbench={handleOpenWorkbench} />
          )
        )}
        {currentScreen === "applications" && (
          <ApplicationsScreen onSelectApplication={handleSelectApplication} />
        )}
        {currentScreen === "application-detail" && selectedAppId && (
          <ApplicationDetailScreen
            applicationId={selectedAppId}
            onBack={() => setCurrentScreen("applications")}
            onOpenWorkbench={handleOpenWorkbench}
          />
        )}
        {currentScreen === "ledger-admin" && (
          <LedgerAdminScreen userRole={currentUser.role} />
        )}
      </main>
    </div>
  );
};
