import React, { useEffect } from "react";
import { useAuth } from "@/context/AuthContext";
import { OnboardingApi } from "./service";
import { Link } from "react-router-dom"; // <-- import Link
import { routes } from "@/lib/routes"; // <-- import routes
import { toast } from "sonner"

export default function OverviewPage() {
    const { user } = useAuth();
  return (
    <>Overview</>
  );
}
