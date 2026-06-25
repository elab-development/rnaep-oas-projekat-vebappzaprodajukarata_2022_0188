import logo from "../assets/LOGO.png";
import { useState } from "react";
import { register } from "../services/authService";
import { Link, useNavigate } from "react-router-dom";

function RegisterPage() {


    const navigate = useNavigate();

    const [formData, setFormData] = useState({
        name: "",
        email: "",
        password: "",
        password_confirmation: "",
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

        if (!formData.name || !formData.email || !formData.password || !formData.password_confirmation) {
            setError("All fields are required.");
            return;
        }

        if (formData.password.length < 8) {
            setError("Password must be at least 8 characters.");
            return;
        }

        if (formData.password !== formData.password_confirmation) {
            setError("Passwords do not match.");
            return;
        }

        try {
            await register(formData);

            navigate("/");
        } catch {
            setError("Registration failed.");
        }
    };


    return (
        <div className="min-h-screen bg-slate-950 flex items-center justify-center px-4">
            {/* Logo */}
            <div className="absolute top-6 left-6">
                <img src={logo} alt="ticketGo" className="h-28 w-auto" />
            </div>

            {/* Register Card */}
            <div className="w-full max-w-md rounded-3xl bg-white p-8 shadow-2xl">
                <h1 className="text-center text-3xl font-bold text-slate-900">
                    Create Account
                </h1>

                <p className="mt-2 text-center text-slate-500">
                    Join ticketGo and discover amazing events.
                </p>

                <form onSubmit={handleSubmit} className="mt-8 space-y-5">
                    <div>
                        <label className="mb-2 block text-sm font-medium text-slate-700">
                            Name
                        </label>
                        <input
                            type="text"
                            name="name"
                            value={formData.name}
                            onChange={handleChange}
                            placeholder="John Doe"
                            className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100"
                        />
                    </div>

                    <div>
                        <label className="mb-2 block text-sm font-medium text-slate-700">
                            Email
                        </label>
                        <input
                            type="email"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            placeholder="you@example.com"
                            className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100"
                        />
                    </div>

                    <div>
                        <label className="mb-2 block text-sm font-medium text-slate-700">
                            Password
                        </label>
                        <input
                            type="password"
                            name="password"
                            value={formData.password}
                            onChange={handleChange}
                            placeholder="Enter password"
                            className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100"
                        />
                    </div>

                    <div>
                        <label className="mb-2 block text-sm font-medium text-slate-700">
                            Confirm Password
                        </label>
                        <input
                            type="password"
                            name="password_confirmation"
                            value={formData.password_confirmation}
                            onChange={handleChange}
                            placeholder="Confirm password"
                            className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100"
                        />
                    </div>
                    {error && (
                        <p className="rounded-xl bg-red-50 px-4 py-3 text-sm text-red-600">
                            {error}
                        </p>
                    )}
                    <button
                        type="submit"
                        className="w-full rounded-xl bg-blue-600 py-3 font-semibold text-white transition hover:bg-blue-700"
                    >
                        Create Account
                    </button>
                </form>


                <p className="mt-6 text-center text-sm text-slate-500">
                    Already have an account?{" "}
                    <Link
                        to="/"
                        className="font-semibold text-blue-600 hover:underline"
                    >
                        Login
                    </Link>
                </p>
            </div>
        </div>
    );
}

export default RegisterPage;