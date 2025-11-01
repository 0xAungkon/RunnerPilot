import React, { useEffect } from "react";
import { useAuth } from "@/context/AuthContext";

const Sample: React.FC = () => {
    const { user } = useAuth();
    useEffect(() => {
        console.log("User info:", user);
    }, [user]);
    return <>Coming Soon.......</>;
};

export default Sample;
