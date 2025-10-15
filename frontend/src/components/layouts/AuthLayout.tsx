import type { FC } from "react";
import { Outlet } from "react-router-dom";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import ThemeSwitcher from "../utils/theme-switcher";

interface AuthLayoutProps {
    title: string;
}

const AuthLayout: FC<AuthLayoutProps> = ({ title }) => {
    return (
        <div className="flex min-h-screen items-center justify-center">
            <Card className="w-full max-w-md shadow-lg relative">
                <CardHeader>
                    <h2 className="text-2xl font-bold text-center">{title}</h2>
                    <div className="absolute top-4 right-4">
                        <ThemeSwitcher />
                    </div>
                </CardHeader>
                <CardContent>
                    <Outlet />
                </CardContent>
            </Card>
        </div>
    );
};

export default AuthLayout;
