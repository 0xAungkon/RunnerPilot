import React, { useEffect } from "react";
import { useAuth } from "@/context/AuthContext";
import { OnboardingApi } from "./service";
import { Link } from "react-router-dom"; // <-- import Link
import { routes } from "@/lib/routes"; // <-- import routes
import { toast } from "sonner"

const Sample: React.FC = () => {
    const { user } = useAuth();
    useEffect(() => {
        console.log("User info:", user);
    }, [user]);
    return <></>;
};

export default Sample;
