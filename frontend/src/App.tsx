import { Route, Routes } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import AppRoutes from "./Routes";
import { ThemeProvider } from "@/components/providers/ThemeProvider"
import { ToastProvider } from "@/components/providers/ToastProvider";

const App: React.FC = () => {
  return (
    <ThemeProvider defaultTheme="dark" storageKey="theme-ui-mode">
      <ToastProvider>
        <AuthProvider>
          <Routes>
            <Route path="/*" element={<AppRoutes />} />
          </Routes>
        </AuthProvider>
      </ToastProvider>
    </ThemeProvider>
  );
};

export default App;
