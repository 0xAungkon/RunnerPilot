import React, { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { loginApi } from "./service";
import { Spinner } from "@/components/ui/spinner";
import { toast } from "sonner";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Link, useNavigate } from "react-router-dom";
import { routes } from "@/lib/routes";

const LoginPage: React.FC = () => {
    const [form, setForm] = useState({ username: "", password: "" });
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setForm({ ...form, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        const res = await loginApi(form);
        setLoading(false);
        if (res.success && res.data) {
            login(res.data.access_token);
            toast.success("Login successful!");
            navigate(routes.dashboard);
        } else {
            toast.error(res.message);
        }
    };

    return (
        <>
            <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                    <Label htmlFor="username">Username</Label>
                    <Input
                        id="username"
                        name="username"
                        type="text"
                        value={form.username}
                        onChange={handleChange}
                        required
                        placeholder="Enter your username"
                        className="mt-2"
                    />
                </div>
                <div>
                    <Label htmlFor="password">Password</Label>
                    <Input
                        id="password"
                        name="password"
                        type="password"
                        value={form.password}
                        onChange={handleChange}
                        required
                        placeholder="Enter your password"
                        className="mt-2"
                    />
                </div>
                <Button type="submit" className="w-full" disabled={loading}>
                    {loading ? <Spinner /> : "Login"}
                </Button>
            </form>
            <p className="mt-4 text-center text-sm text-gray-600">
                Don't have an account?{" "}
                <Link to={routes.register} className="text-blue-500 hover:underline">
                    Register Here
                </Link>
            </p>
        </>
    );
};

export default LoginPage;
