import React, { useEffect, useState } from "react";
import type { ReactNode } from "react";
import { Routes, Route, Navigate } from "react-router-dom";

import { routes } from "./lib/routes";

import { useAuth } from "@/context/AuthContext";
import ErrorPage from "./pages/ErrorPage";
import LoginPage from "@/pages/Authentication/Login";
import TestPage from "./pages/Dashboard/Test";  
import AuthLayout from "./components/layouts/AuthLayout";
import DashboardLayout from "./components/layouts/DashboardLayout";
import OverviewPage from "./pages/Dashboard/Overview";
import RunnersPage from "./pages/Dashboard/Runners";

interface ProtectedRouteProps {
  children: ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { token } = useAuth();
  return token ? <>{children}</> : <Navigate to={routes.login} replace />;
};

const AppRoutes: React.FC = () => {
  const [serverUp, setServerUp] = useState<boolean>(true);

  useEffect(() => {
    const checkServer = async () => {
      try {
        const res = await fetch(`${import.meta.env.VITE_API_BASE_URL as string}`);
        if (!res.ok) setServerUp(false);
      } catch {
        setServerUp(false);
      }
    };
    checkServer();
  }, [window]);


  if (!serverUp) {
    if (import.meta.env.VITE_ENV !== "development") {
      return (
        <ErrorPage 
                title="We Are Under Maintenance."
                smallTitle="408 ERROR"
                description="Our servers are currently down for maintenance. Please try again later."
              />
      );
    } 
    else{
      console.warn("Backend server is down. Please ensure the backend is running.");
    }
  }

  return (
    <Routes>
        <Route element={<AuthLayout title="Login" />}>
          <Route element={<LoginPage />} path={routes.login} />
          <Route element={<LoginPage />} path="/" />
        </Route>
        <Route>
          <Route element={<TestPage />} path={routes.test} />
        </Route>
        <Route element={<ProtectedRoute><DashboardLayout title="Sample" /></ProtectedRoute>}>
          {/* <Route element={<OverviewPage />} path={routes.dashboardRoot} />
          <Route element={<OverviewPage />} path={routes.dashboard} /> */}
          {/* Comming Soon */}
        </Route>
        <Route element={<ProtectedRoute><DashboardLayout title="Runners" /></ProtectedRoute>}>
          <Route element={<RunnersPage />} path={routes.runners} />
          <Route element={<RunnersPage />} path={routes.dashboardRoot} />
          <Route element={<RunnersPage />} path={routes.dashboard} />
        </Route>

      {/* <Route
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route element={<Dashboard />} path={routes.dashboardRoot} />
        <Route element={<Dashboard />} path={routes.dashboard} />
        <Route element={<PlartformApi />} path={routes.platformApi} />
      </Route>

      <Route
        element={
          <ProtectedRoute>
            <CanvasLayout />
          </ProtectedRoute>
        }
      >
        <Route element={<Envelope />} path={routes.envelope} />
        <Route
          element={<DragNDropTemplateBuilder />}
          path={routes.dragNDropTemplateBuilder}
        />
        <Route element={<PreviewOrSignPage />} path={routes.sign} />
      </Route> */}

      <Route
        element={
          <ErrorPage 
            title="Page Not Found"
            smallTitle="404 ERROR"
            description="The page you're looking for doesn't exist."
          />
        }
        path="*"
      />
    </Routes>
  );
};

export default AppRoutes;
