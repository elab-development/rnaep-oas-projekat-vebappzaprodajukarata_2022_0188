import logo from "../assets/LOGO.png";
import { useState } from "react";
import { login } from "../services/authService";
import { Link, useNavigate } from "react-router-dom";

function LoginPage() {

    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        email: "",
        password: "",
    });

    const [error, setError] = useState("");

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;

        setFormData({
            ...formData,
            [name]: value,
        });
    };

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setError("");

        if (!formData.email || !formData.password) {
            setError("All fields are required.");
            return;
        }

        try {
            const response = await login(formData);

            localStorage.setItem("token", response.token);
            localStorage.setItem("user", JSON.stringify(response.user));

            localStorage.setItem("token", response.token);
            localStorage.setItem("user", JSON.stringify(response.user));
            localStorage.removeItem("guest");

            const role = response.user.roles[0];

            if (role === "admin") {
                navigate("/admin-dashboard");
            } else {
                navigate("/dashboard");
            }
        } catch {
            setError("Invalid email or password.");
        }
    };

    const handleGuestMode = () => {
        localStorage.setItem("guest", "true");
        localStorage.removeItem("token");
        localStorage.removeItem("user");

        navigate("/events");
    };

    return (
        <div className="min-h-screen bg-slate-950 flex items-center justify-center px-4">
            <div className="absolute top-6 left-6">
                <img src={logo} alt="ticketGo" className="h-28 w-auto" />
            </div>
            <div className="w-full max-w-md rounded-3xl bg-white p-8 shadow-2xl">
                <h1 className="text-center text-4xl font-bold text-blue-600">
                    ticketGo
                </h1>

                <h2 className="mt-8 text-center text-2xl font-bold text-slate-900">
                    Welcome back
                </h2>

                <form onSubmit={handleSubmit} className="mt-8 space-y-5">
                    <input
                        type="email"
                        name="email"
                        value={formData.email}
                        onChange={handleChange}
                        placeholder="you@example.com"
                        className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100"
                    />

                    <input
                        type="password"
                        name="password"
                        value={formData.password}
                        onChange={handleChange}
                        placeholder="Enter password"
                        className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100"
                    />
                    {error && (
                        <div className="rounded-xl bg-red-50 p-3 text-sm text-red-600">
                            {error}
                        </div>
                    )}

                    <button type="submit" className="w-full rounded-xl bg-blue-600 py-3 font-semibold text-white hover:bg-blue-700">
                        Login
                    </button>

                    <button
                        type="button"
                        onClick={handleGuestMode}
                        className="w-full rounded-xl border border-slate-300 py-3 font-semibold text-slate-700 hover:bg-slate-100"
                    >
                        Continue as Guest
                    </button>
                </form>

                <p className="mt-6 text-center text-sm text-slate-500">
                    Don&apos;t have an account?{" "}
                    <Link
                        to="/register"
                        className="font-semibold text-blue-600 hover:underline"
                    >
                        Register
                    </Link>
                </p>
            </div>
        </div>
    );
}

export default LoginPage;