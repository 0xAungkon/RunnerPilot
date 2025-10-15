import React, { useState } from "react";
import { registerApi } from "./service";
import { Spinner } from "@/components/ui/spinner";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Link } from "react-router-dom"; // <-- import Link
import { routes } from "@/lib/routes"; // <-- import routes
import { toast } from "sonner"

const RegistrationPage: React.FC = () => {
        const [form, setForm] = useState({
            firstname: "",
            lastname: "",
            email: "",
            password: "",
        });
        const [loading, setLoading] = useState(false);

        const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
            setForm({ ...form, [e.target.name]: e.target.value });
        };

        const handleSubmit = async (e: React.FormEvent) => {
            e.preventDefault();
            setLoading(true);
            const res = await registerApi(form);
            setLoading(false);
            if (res.success) {
                toast.success(res.data.detail || "Registration successful!");
                setTimeout(() => {
                    window.location.href = routes.login;
                }, 2000);
            } else {
                toast.error(res.message);
            }
        };

        return (
            <>
                <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                        <Label htmlFor="firstname">First Name</Label>
                        <Input
                            id="firstname"
                            name="firstname"
                            type="text"
                            value={form.firstname}
                            onChange={handleChange}
                            required
                            placeholder="Enter your first name"
                            className="mt-2"
                        />
                    </div>
                    <div>
                        <Label htmlFor="lastname">Last Name</Label>
                        <Input
                            id="lastname"
                            name="lastname"
                            type="text"
                            value={form.lastname}
                            onChange={handleChange}
                            required
                            placeholder="Enter your last name"
                            className="mt-2"
                        />
                    </div>
                    <div>
                        <Label htmlFor="email">Email</Label>
                        <Input
                            id="email"
                            name="email"
                            type="email"
                            value={form.email}
                            onChange={handleChange}
                            required
                            placeholder="Enter your email"
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
                        {loading ? <Spinner /> : "Register"}
                    </Button>
                </form>
                <p className="mt-4 text-center text-sm text-gray-600">
                    Already have an account?{" "}
                    <Link to={routes.login} className="text-blue-500 hover:underline">
                        Login
                    </Link>
                </p>
            </>
        );
};

export default RegistrationPage;
