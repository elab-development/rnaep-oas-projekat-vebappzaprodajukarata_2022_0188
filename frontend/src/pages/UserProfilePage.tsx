import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import logo from "../assets/LOGO.png";

type User = {
  id: number;
  name: string;
  email: string;
  roles?: string[];
};

function UserProfilePage() {
  const [user, setUser] = useState<User | null>(null);
  const [isEditing, setIsEditing] = useState(false);

  const [formData, setFormData] = useState({
    name: "",
    email: "",
  });

  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const token = localStorage.getItem("token");
  const storedUser = JSON.parse(localStorage.getItem("user") || "{}");
  const userId = storedUser.id;

  useEffect(() => {
    if (!token || !userId) {
      setErrorMessage("User is not logged in.");
      return;
    }

    fetch(`http://localhost:8000/api/users/${userId}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then(async (res) => {
        if (!res.ok) {
          throw new Error("Failed to load profile.");
        }

        return res.json();
      })
      .then((data) => {
        setUser(data);
        setFormData({
          name: data.name || "",
          email: data.email || "",
        });
      })
      .catch(() => {
        setErrorMessage("Failed to load profile.");
      });
  }, [token, userId]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();

    setSuccessMessage("");
    setErrorMessage("");

    if (!formData.name.trim() || !formData.email.trim()) {
      setErrorMessage("Name and email are required.");
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/users/${userId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          name: formData.name,
          email: formData.email,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        setErrorMessage(errorData.detail || "Failed to update profile.");
        return;
      }

      const updatedUser = await response.json();

      setUser(updatedUser);
      localStorage.setItem("user", JSON.stringify(updatedUser));

      setIsEditing(false);
      setSuccessMessage("Profile updated successfully.");
    } catch {
      setErrorMessage("Failed to update profile.");
    }
  };

  if (!user && !errorMessage) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950 text-white">
        Loading profile...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <header className="flex items-center justify-between border-b border-slate-800 px-8 py-5">
        <img src={logo} alt="ticketGo" className="h-20 w-auto" />

        <Link
          to="/dashboard"
          className="rounded-xl bg-blue-600 px-5 py-2 font-semibold hover:bg-blue-700"
        >
          My Dashboard
        </Link>
      </header>

      <main className="mx-auto max-w-4xl px-8 py-10">
        <h1 className="mb-8 text-4xl font-bold">My Profile</h1>

        {successMessage && (
          <div className="mb-6 rounded-xl bg-green-600 px-5 py-3 font-semibold">
            {successMessage}
          </div>
        )}

        {errorMessage && (
          <div className="mb-6 rounded-xl bg-red-600 px-5 py-3 font-semibold">
            {errorMessage}
          </div>
        )}

        {user && (
          <div className="rounded-3xl bg-slate-900 p-8 shadow-xl">
            <div className="mb-8 flex items-center gap-6">
              <div className="flex h-24 w-24 items-center justify-center rounded-full bg-blue-600 text-4xl font-bold">
                {user.name ? user.name.charAt(0).toUpperCase() : "U"}
              </div>

              <div>
                <h2 className="text-3xl font-bold">{user.name}</h2>
                <p className="text-slate-400">{user.email}</p>
              </div>
            </div>

            <div className="mb-8 grid gap-4 md:grid-cols-2">
              <div className="rounded-2xl bg-slate-800 p-5">
                <p className="text-sm text-slate-400">Name</p>
                <p className="mt-1 text-xl font-semibold">{user.name}</p>
              </div>

              <div className="rounded-2xl bg-slate-800 p-5">
                <p className="text-sm text-slate-400">Email</p>
                <p className="mt-1 text-xl font-semibold">{user.email}</p>
              </div>

              <div className="rounded-2xl bg-slate-800 p-5">
                <p className="text-sm text-slate-400">Role</p>
                <p className="mt-1 text-xl font-semibold">
                  {user.roles?.join(", ") || "user"}
                </p>
              </div>

              <div className="rounded-2xl bg-slate-800 p-5">
                <p className="text-sm text-slate-400">Account status</p>
                <p className="mt-1 text-xl font-semibold text-green-400">
                  Active
                </p>
              </div>
            </div>

            <button
              onClick={() => {
                setIsEditing(true);
                setSuccessMessage("");
                setErrorMessage("");
                setFormData({
                  name: user.name || "",
                  email: user.email || "",
                });
              }}
              className="rounded-xl bg-blue-600 px-6 py-3 font-semibold hover:bg-blue-700"
            >
              Edit Profile
            </button>
          </div>
        )}

        {isEditing && user && (
          <div className="fixed inset-0 flex items-center justify-center bg-black/60 px-4">
            <form
              onSubmit={handleSave}
              className="w-full max-w-md rounded-3xl bg-slate-900 p-8 shadow-2xl"
            >
              <h2 className="mb-6 text-2xl font-bold">Edit Profile</h2>

              <label className="mb-2 block text-sm text-slate-300">
                Name
              </label>
              <input
                name="name"
                value={formData.name}
                onChange={handleChange}
                className="mb-4 w-full rounded-xl bg-slate-800 px-4 py-3 text-white outline-none"
              />

              <label className="mb-2 block text-sm text-slate-300">
                Email
              </label>
              <input
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                className="mb-6 w-full rounded-xl bg-slate-800 px-4 py-3 text-white outline-none"
              />

              <div className="flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => {
                    setIsEditing(false);
                    setErrorMessage("");
                    setFormData({
                      name: user.name || "",
                      email: user.email || "",
                    });
                  }}
                  className="rounded-xl bg-slate-700 px-5 py-2 font-semibold hover:bg-slate-600"
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="rounded-xl bg-blue-600 px-5 py-2 font-semibold hover:bg-blue-700"
                >
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        )}
      </main>
    </div>
  );
}

export default UserProfilePage;