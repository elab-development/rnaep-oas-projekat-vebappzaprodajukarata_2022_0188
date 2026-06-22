import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import EventsSection from "./EventsSection";

interface User {
  id: number;
  name: string;
  email: string;
  roles: string[];
}

const API = "http://localhost:8000/api";

function AdminDashboardPage() {
  const navigate = useNavigate();
  const [section, setSection] = useState("users");

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    navigate("/");
  };

  return (
    <div className="flex min-h-screen bg-slate-50">
      <aside className="flex w-64 flex-col bg-slate-950 text-white">
        <div className="px-6 py-6">
          <span className="text-2xl font-bold text-blue-500">ticketGo</span>
          <p className="mt-1 text-xs text-slate-400">Admin panel</p>
        </div>
        <nav className="flex-1 space-y-1 px-3">
          <MenuButton label="Korisnici" active={section === "users"} onClick={() => setSection("users")} />
          <MenuButton label="Događaji" active={section === "events"} onClick={() => setSection("events")} />
          <MenuButton label="Karte" active={section === "tickets"} onClick={() => setSection("tickets")} />
          <MenuButton label="Izveštaji" active={section === "reports"} onClick={() => setSection("reports")} />
        </nav>
        <div className="px-3 pb-6">
          <button onClick={handleLogout} className="w-full rounded-xl border border-slate-600 px-4 py-2 text-sm font-semibold hover:bg-slate-800">
            Logout
          </button>
        </div>
      </aside>

      <main className="flex-1 px-8 py-8">
        {section === "users" && <UsersSection />}
        {section === "events" && <EventsSection />}
        {section === "tickets" && <PlaceholderSection title="Karte" servis="Ticket servis" />}
        {section === "reports" && <PlaceholderSection title="Izveštaji o prodaji" servis="Payment servis" />}
      </main>
    </div>
  );
}

function MenuButton({ label, active, onClick }: { label: string; active: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className={`w-full rounded-xl px-4 py-3 text-left font-medium transition ${
        active ? "bg-blue-600 text-white" : "text-slate-300 hover:bg-slate-800"
      }`}
    >
      {label}
    </button>
  );
}

function UsersSection() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ name: "", email: "", password: "", passwordConfirm: "" });
  const [formError, setFormError] = useState("");
  const token = localStorage.getItem("token");

  const loadUsers = async () => {
    const res = await fetch(`${API}/users`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error();
    setUsers(await res.json());
  };

  useEffect(() => {
    loadUsers()
      .catch(() => setError("Ne mogu da učitam korisnike. Da li backend radi?"))
      .finally(() => setLoading(false));
  }, [token]);

  const handleDelete = async (id: number) => {
    if (!window.confirm("Obrisati ovog korisnika?")) return;
    try {
      const res = await fetch(`${API}/users/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error();
      setUsers(users.filter((u) => u.id !== id));
    } catch {
      window.alert("Greška pri brisanju.");
    }
  };

  const handleToggleRole = async (user: User) => {
    const isAdmin = user.roles.includes("admin");
    const endpoint = isAdmin ? "remove-role" : "assign-role";
    const method = isAdmin ? "DELETE" : "POST";
    try {
      const res = await fetch(`${API}/users/${user.id}/${endpoint}`, {
        method,
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({ role: "admin" }),
      });
      if (!res.ok) throw new Error();
      const updated = await res.json();
      setUsers(users.map((u) => (u.id === user.id ? updated : u)));
    } catch {
      window.alert("Greška pri promeni uloge.");
    }
  };

  const handleAddUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError("");
    try {
      const res = await fetch(`${API}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: form.name,
          email: form.email,
          password: form.password,
          password_confirmation: form.passwordConfirm,
        }),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(typeof data.detail === "string" ? data.detail : "Greška pri dodavanju.");
      }
      await loadUsers();
      setShowModal(false);
      setForm({ name: "", email: "", password: "", passwordConfirm: "" });
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "Greška pri dodavanju korisnika.");
    }
  };

  const totalUsers = users.length;
  const adminCount = users.filter((u) => u.roles.includes("admin")).length;
  const inputClass = "w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100";

  return (
    <div>
      <h1 className="mb-8 text-3xl font-bold text-slate-900">Upravljanje korisnicima</h1>

      <div className="mb-8 grid grid-cols-1 gap-6 sm:grid-cols-2">
        <StatCard label="Ukupno korisnika" value={totalUsers} />
        <StatCard label="Administratori" value={adminCount} />
      </div>

      <div className="overflow-hidden rounded-2xl bg-white shadow-lg">
        <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
          <h2 className="text-lg font-semibold text-slate-900">Lista korisnika</h2>
          <button
            onClick={() => setShowModal(true)}
            className="rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700"
          >
            + Dodaj korisnika
          </button>
        </div>
        {loading ? (
          <p className="px-6 py-8 text-center text-slate-500">Učitavanje...</p>
        ) : error ? (
          <p className="px-6 py-8 text-center text-red-600">{error}</p>
        ) : (
          <table className="w-full text-left">
            <thead className="bg-slate-50 text-sm text-slate-500">
              <tr>
                <th className="px-6 py-3 font-medium">ID</th>
                <th className="px-6 py-3 font-medium">Ime</th>
                <th className="px-6 py-3 font-medium">Email</th>
                <th className="px-6 py-3 font-medium">Uloga</th>
                <th className="px-6 py-3 font-medium">Akcije</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id} className="border-t border-slate-100 hover:bg-slate-50">
                  <td className="px-6 py-4 text-slate-700">{user.id}</td>
                  <td className="px-6 py-4 font-medium text-slate-900">{user.name}</td>
                  <td className="px-6 py-4 text-slate-600">{user.email}</td>
                  <td className="px-6 py-4">
                    <span className={`rounded-full px-3 py-1 text-xs font-semibold ${
                      user.roles.includes("admin") ? "bg-blue-100 text-blue-700" : "bg-slate-100 text-slate-600"
                    }`}>
                      {user.roles.includes("admin") ? "Admin" : "Korisnik"}
                    </span>
                  </td>
                  <td className="space-x-2 px-6 py-4">
                    <button
                      onClick={() => handleToggleRole(user)}
                      className="rounded-lg bg-blue-50 px-3 py-1 text-sm font-semibold text-blue-600 hover:bg-blue-100"
                    >
                      {user.roles.includes("admin") ? "Ukloni admin" : "Učini adminom"}
                    </button>
                    <button
                      onClick={() => handleDelete(user.id)}
                      className="rounded-lg bg-red-50 px-3 py-1 text-sm font-semibold text-red-600 hover:bg-red-100"
                    >
                      Obriši
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Modal za dodavanje korisnika */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
          <div className="w-full max-w-md rounded-2xl bg-white p-8 shadow-2xl">
            <h2 className="mb-6 text-2xl font-bold text-slate-900">Novi korisnik</h2>
            <form onSubmit={handleAddUser} className="space-y-4">
              <input className={inputClass} placeholder="Ime" value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })} required />
              <input className={inputClass} type="email" placeholder="Email" value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })} required />
              <input className={inputClass} type="password" placeholder="Lozinka (8+ karaktera)" value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })} required />
              <input className={inputClass} type="password" placeholder="Potvrdi lozinku" value={form.passwordConfirm}
                onChange={(e) => setForm({ ...form, passwordConfirm: e.target.value })} required />
              {formError && <p className="text-sm text-red-600">{formError}</p>}
              <div className="flex gap-3 pt-2">
                <button type="submit" className="flex-1 rounded-xl bg-blue-600 py-3 font-semibold text-white hover:bg-blue-700">
                  Dodaj
                </button>
                <button type="button" onClick={() => { setShowModal(false); setFormError(""); }}
                  className="flex-1 rounded-xl border border-slate-300 py-3 font-semibold text-slate-700 hover:bg-slate-100">
                  Otkaži
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

function PlaceholderSection({ title, servis }: { title: string; servis: string }) {
  return (
    <div>
      <h1 className="mb-8 text-3xl font-bold text-slate-900">{title}</h1>
      <div className="rounded-2xl bg-white p-12 text-center shadow-lg">
        <p className="text-lg font-semibold text-slate-700">Uskoro</p>
        <p className="mt-2 text-slate-500">
          Ova sekcija prikazivaće podatke iz: <strong>{servis}</strong>.
          <br />
          Biće povezana kada API bude spreman.
        </p>
      </div>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-2xl bg-white p-6 shadow-lg">
      <p className="text-sm text-slate-500">{label}</p>
      <p className="mt-2 text-3xl font-bold text-blue-600">{value}</p>
    </div>
  );
}

export default AdminDashboardPage;