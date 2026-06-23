import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  getAllEvents, createEvent, updateEvent, deleteEvent, cancelEvent,
  getAllVenues, createVenue, deleteVenue,
  getAllCategories, createCategory, deleteCategory,
  type AdminEvent, type Venue, type Category
} from "../services/eventAdminService";

import {
  getAllPayments, getAllRefunds, getAllTransactions,
  type Payment, type Refund, type Transaction
} from "../services/paymentAdminService";

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
        {section === "events" && <EventsSection />}        {section === "tickets" && <PlaceholderSection title="Karte" servis="Ticket servis" />}
        {section === "reports" && <PaymentReportsSection />}      </main>
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

function EventsSection() {
  const [tab, setTab] = useState<"events" | "venues" | "categories">("events");
  const [events, setEvents] = useState<AdminEvent[]>([]);
  const [venues, setVenues] = useState<Venue[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [showEventModal, setShowEventModal] = useState(false);
  const [editingEvent, setEditingEvent] = useState<AdminEvent | null>(null);
  const [eventForm, setEventForm] = useState({
    title: "", description: "", start_time: "", end_time: "", venue_id: "", category_id: ""
  });

  const [showVenueModal, setShowVenueModal] = useState(false);
  const [venueForm, setVenueForm] = useState({ name: "", address: "", city: "", capacity: "" });

  const [showCategoryModal, setShowCategoryModal] = useState(false);
  const [categoryForm, setCategoryForm] = useState({ name: "", description: "" });

  const loadAll = async () => {
    const [e, v, c] = await Promise.all([getAllEvents(), getAllVenues(), getAllCategories()]);
    setEvents(e);
    setVenues(v);
    setCategories(c);
  };

  useEffect(() => {
    loadAll()
      .catch(() => setError("Ne mogu da učitam podatke. Da li backend radi?"))
      .finally(() => setLoading(false));
  }, []);

  const venueName = (id: number) => venues.find((v) => v.id === id)?.name || `#${id}`;
  const categoryName = (id: number) => categories.find((c) => c.id === id)?.name || `#${id}`;

  // ---------------- EVENT HANDLERS ----------------

  const openCreateEvent = () => {
    setEditingEvent(null);
    setEventForm({ title: "", description: "", start_time: "", end_time: "", venue_id: "", category_id: "" });
    setShowEventModal(true);
  };

  const openEditEvent = (ev: AdminEvent) => {
    setEditingEvent(ev);
    setEventForm({
      title: ev.title,
      description: ev.description || "",
      start_time: ev.start_time.slice(0, 16),
      end_time: ev.end_time.slice(0, 16),
      venue_id: String(ev.venue_id),
      category_id: String(ev.category_id),
    });
    setShowEventModal(true);
  };

  const handleSaveEvent = async (e: React.FormEvent) => {
    e.preventDefault();
    const payload = {
      title: eventForm.title,
      description: eventForm.description || undefined,
      start_time: eventForm.start_time,
      end_time: eventForm.end_time,
      venue_id: Number(eventForm.venue_id),
      category_id: Number(eventForm.category_id),
    };
    try {
      if (editingEvent) {
        const updated = await updateEvent(editingEvent.id, payload);
        setEvents(events.map((ev) => (ev.id === updated.id ? updated : ev)));
      } else {
        const created = await createEvent(payload);
        setEvents([...events, created]);
      }
      setShowEventModal(false);
    } catch (err) {
      window.alert(err instanceof Error ? err.message : "Greška.");
    }
  };

  const handleDeleteEvent = async (id: number) => {
    if (!window.confirm("Obrisati ovaj događaj?")) return;
    try {
      await deleteEvent(id);
      setEvents(events.filter((ev) => ev.id !== id));
    } catch {
      window.alert("Greška pri brisanju.");
    }
  };

  const handleCancelEvent = async (id: number) => {
    if (!window.confirm("Otkazati ovaj događaj?")) return;
    try {
      const updated = await cancelEvent(id);
      setEvents(events.map((ev) => (ev.id === id ? updated : ev)));
    } catch {
      window.alert("Greška pri otkazivanju.");
    }
  };

  // ---------------- VENUE HANDLERS ----------------

  const handleSaveVenue = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const created = await createVenue({
        name: venueForm.name,
        address: venueForm.address,
        city: venueForm.city,
        capacity: Number(venueForm.capacity),
      });
      setVenues([...venues, created]);
      setShowVenueModal(false);
      setVenueForm({ name: "", address: "", city: "", capacity: "" });
    } catch {
      window.alert("Greška pri kreiranju lokacije.");
    }
  };

  const handleDeleteVenue = async (id: number) => {
    if (!window.confirm("Obrisati ovu lokaciju?")) return;
    try {
      await deleteVenue(id);
      setVenues(venues.filter((v) => v.id !== id));
    } catch {
      window.alert("Greška pri brisanju lokacije.");
    }
  };

  // ---------------- CATEGORY HANDLERS ----------------

  const handleSaveCategory = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const created = await createCategory({
        name: categoryForm.name,
        description: categoryForm.description || undefined,
      });
      setCategories([...categories, created]);
      setShowCategoryModal(false);
      setCategoryForm({ name: "", description: "" });
    } catch {
      window.alert("Greška pri kreiranju kategorije.");
    }
  };

  const handleDeleteCategory = async (id: number) => {
    if (!window.confirm("Obrisati ovu kategoriju?")) return;
    try {
      await deleteCategory(id);
      setCategories(categories.filter((c) => c.id !== id));
    } catch {
      window.alert("Greška pri brisanju kategorije.");
    }
  };

  const inputClass = "w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100";

  if (loading) return <p className="px-6 py-8 text-center text-slate-500">Učitavanje...</p>;
  if (error) return <p className="px-6 py-8 text-center text-red-600">{error}</p>;

  return (
    <div>
      <h1 className="mb-8 text-3xl font-bold text-slate-900">Događaji</h1>

      <div className="mb-6 flex gap-2">
        <TabButton label="Događaji" active={tab === "events"} onClick={() => setTab("events")} />
        <TabButton label="Lokacije" active={tab === "venues"} onClick={() => setTab("venues")} />
        <TabButton label="Kategorije" active={tab === "categories"} onClick={() => setTab("categories")} />
      </div>

      {/* ---------------- EVENTS TAB ---------------- */}
      {tab === "events" && (
        <div className="overflow-hidden rounded-2xl bg-white shadow-lg">
          <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
            <h2 className="text-lg font-semibold text-slate-900">Lista događaja</h2>
            <button onClick={openCreateEvent} className="rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700">
              + Novi događaj
            </button>
          </div>
          <table className="w-full text-left">
            <thead className="bg-slate-50 text-sm text-slate-500">
              <tr>
                <th className="px-6 py-3 font-medium">Naziv</th>
                <th className="px-6 py-3 font-medium">Lokacija</th>
                <th className="px-6 py-3 font-medium">Kategorija</th>
                <th className="px-6 py-3 font-medium">Status</th>
                <th className="px-6 py-3 font-medium">Akcije</th>
              </tr>
            </thead>
            <tbody>
              {events.map((ev) => (
                <tr key={ev.id} className="border-t border-slate-100 hover:bg-slate-50">
                  <td className="px-6 py-4 font-medium text-slate-900">{ev.title}</td>
                  <td className="px-6 py-4 text-slate-600">{venueName(ev.venue_id)}</td>
                  <td className="px-6 py-4 text-slate-600">{categoryName(ev.category_id)}</td>
                  <td className="px-6 py-4">
                    <span className={`rounded-full px-3 py-1 text-xs font-semibold ${
                      ev.status === "cancelled" ? "bg-red-100 text-red-700" : "bg-green-100 text-green-700"
                    }`}>
                      {ev.status}
                    </span>
                  </td>
                  <td className="space-x-2 px-6 py-4">
                    <button onClick={() => openEditEvent(ev)} className="rounded-lg bg-blue-50 px-3 py-1 text-sm font-semibold text-blue-600 hover:bg-blue-100">
                      Izmeni
                    </button>
                    {ev.status !== "cancelled" && (
                      <button onClick={() => handleCancelEvent(ev.id)} className="rounded-lg bg-amber-50 px-3 py-1 text-sm font-semibold text-amber-600 hover:bg-amber-100">
                        Otkaži
                      </button>
                    )}
                    <button onClick={() => handleDeleteEvent(ev.id)} className="rounded-lg bg-red-50 px-3 py-1 text-sm font-semibold text-red-600 hover:bg-red-100">
                      Obriši
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* ---------------- VENUES TAB ---------------- */}
      {tab === "venues" && (
        <div className="overflow-hidden rounded-2xl bg-white shadow-lg">
          <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
            <h2 className="text-lg font-semibold text-slate-900">Lokacije</h2>
            <button onClick={() => setShowVenueModal(true)} className="rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700">
              + Nova lokacija
            </button>
          </div>
          <table className="w-full text-left">
            <thead className="bg-slate-50 text-sm text-slate-500">
              <tr>
                <th className="px-6 py-3 font-medium">Naziv</th>
                <th className="px-6 py-3 font-medium">Adresa</th>
                <th className="px-6 py-3 font-medium">Grad</th>
                <th className="px-6 py-3 font-medium">Kapacitet</th>
                <th className="px-6 py-3 font-medium">Akcije</th>
              </tr>
            </thead>
            <tbody>
              {venues.map((v) => (
                <tr key={v.id} className="border-t border-slate-100 hover:bg-slate-50">
                  <td className="px-6 py-4 font-medium text-slate-900">{v.name}</td>
                  <td className="px-6 py-4 text-slate-600">{v.address}</td>
                  <td className="px-6 py-4 text-slate-600">{v.city}</td>
                  <td className="px-6 py-4 text-slate-600">{v.capacity}</td>
                  <td className="px-6 py-4">
                    <button onClick={() => handleDeleteVenue(v.id)} className="rounded-lg bg-red-50 px-3 py-1 text-sm font-semibold text-red-600 hover:bg-red-100">
                      Obriši
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* ---------------- CATEGORIES TAB ---------------- */}
      {tab === "categories" && (
        <div className="overflow-hidden rounded-2xl bg-white shadow-lg">
          <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
            <h2 className="text-lg font-semibold text-slate-900">Kategorije</h2>
            <button onClick={() => setShowCategoryModal(true)} className="rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700">
              + Nova kategorija
            </button>
          </div>
          <table className="w-full text-left">
            <thead className="bg-slate-50 text-sm text-slate-500">
              <tr>
                <th className="px-6 py-3 font-medium">Naziv</th>
                <th className="px-6 py-3 font-medium">Opis</th>
                <th className="px-6 py-3 font-medium">Akcije</th>
              </tr>
            </thead>
            <tbody>
              {categories.map((c) => (
                <tr key={c.id} className="border-t border-slate-100 hover:bg-slate-50">
                  <td className="px-6 py-4 font-medium text-slate-900">{c.name}</td>
                  <td className="px-6 py-4 text-slate-600">{c.description || "—"}</td>
                  <td className="px-6 py-4">
                    <button onClick={() => handleDeleteCategory(c.id)} className="rounded-lg bg-red-50 px-3 py-1 text-sm font-semibold text-red-600 hover:bg-red-100">
                      Obriši
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* ---------------- EVENT MODAL ---------------- */}
      {showEventModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
          <div className="w-full max-w-md rounded-2xl bg-white p-8 shadow-2xl">
            <h2 className="mb-6 text-2xl font-bold text-slate-900">{editingEvent ? "Izmeni događaj" : "Novi događaj"}</h2>
            <form onSubmit={handleSaveEvent} className="space-y-4">
              <input className={inputClass} placeholder="Naziv" value={eventForm.title}
                onChange={(e) => setEventForm({ ...eventForm, title: e.target.value })} required />
              <textarea className={inputClass} placeholder="Opis (opciono)" value={eventForm.description}
                onChange={(e) => setEventForm({ ...eventForm, description: e.target.value })} />
              <input className={inputClass} type="datetime-local" value={eventForm.start_time}
                onChange={(e) => setEventForm({ ...eventForm, start_time: e.target.value })} required />
              <input className={inputClass} type="datetime-local" value={eventForm.end_time}
                onChange={(e) => setEventForm({ ...eventForm, end_time: e.target.value })} required />
              <select className={inputClass} value={eventForm.venue_id}
                onChange={(e) => setEventForm({ ...eventForm, venue_id: e.target.value })} required>
                <option value="">Izaberi lokaciju</option>
                {venues.map((v) => <option key={v.id} value={v.id}>{v.name}</option>)}
              </select>
              <select className={inputClass} value={eventForm.category_id}
                onChange={(e) => setEventForm({ ...eventForm, category_id: e.target.value })} required>
                <option value="">Izaberi kategoriju</option>
                {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
              <div className="flex gap-3 pt-2">
                <button type="submit" className="flex-1 rounded-xl bg-blue-600 py-3 font-semibold text-white hover:bg-blue-700">
                  Sačuvaj
                </button>
                <button type="button" onClick={() => setShowEventModal(false)}
                  className="flex-1 rounded-xl border border-slate-300 py-3 font-semibold text-slate-700 hover:bg-slate-100">
                  Otkaži
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ---------------- VENUE MODAL ---------------- */}
      {showVenueModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
          <div className="w-full max-w-md rounded-2xl bg-white p-8 shadow-2xl">
            <h2 className="mb-6 text-2xl font-bold text-slate-900">Nova lokacija</h2>
            <form onSubmit={handleSaveVenue} className="space-y-4">
              <input className={inputClass} placeholder="Naziv" value={venueForm.name}
                onChange={(e) => setVenueForm({ ...venueForm, name: e.target.value })} required />
              <input className={inputClass} placeholder="Adresa" value={venueForm.address}
                onChange={(e) => setVenueForm({ ...venueForm, address: e.target.value })} required />
              <input className={inputClass} placeholder="Grad" value={venueForm.city}
                onChange={(e) => setVenueForm({ ...venueForm, city: e.target.value })} required />
              <input className={inputClass} type="number" placeholder="Kapacitet" value={venueForm.capacity}
                onChange={(e) => setVenueForm({ ...venueForm, capacity: e.target.value })} required />
              <div className="flex gap-3 pt-2">
                <button type="submit" className="flex-1 rounded-xl bg-blue-600 py-3 font-semibold text-white hover:bg-blue-700">
                  Sačuvaj
                </button>
                <button type="button" onClick={() => setShowVenueModal(false)}
                  className="flex-1 rounded-xl border border-slate-300 py-3 font-semibold text-slate-700 hover:bg-slate-100">
                  Otkaži
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ---------------- CATEGORY MODAL ---------------- */}
      {showCategoryModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
          <div className="w-full max-w-md rounded-2xl bg-white p-8 shadow-2xl">
            <h2 className="mb-6 text-2xl font-bold text-slate-900">Nova kategorija</h2>
            <form onSubmit={handleSaveCategory} className="space-y-4">
              <input className={inputClass} placeholder="Naziv" value={categoryForm.name}
                onChange={(e) => setCategoryForm({ ...categoryForm, name: e.target.value })} required />
              <input className={inputClass} placeholder="Opis (opciono)" value={categoryForm.description}
                onChange={(e) => setCategoryForm({ ...categoryForm, description: e.target.value })} />
              <div className="flex gap-3 pt-2">
                <button type="submit" className="flex-1 rounded-xl bg-blue-600 py-3 font-semibold text-white hover:bg-blue-700">
                  Sačuvaj
                </button>
                <button type="button" onClick={() => setShowCategoryModal(false)}
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

function TabButton({ label, active, onClick }: { label: string; active: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className={`rounded-xl px-4 py-2 text-sm font-semibold transition ${
        active ? "bg-blue-600 text-white" : "bg-white text-slate-600 hover:bg-slate-100"
      }`}
    >
      {label}
    </button>
  );
}

function PaymentReportsSection() {
  const [tab, setTab] = useState<"payments" | "refunds" | "transactions">("payments");
  const [payments, setPayments] = useState<Payment[]>([]);
  const [refunds, setRefunds] = useState<Refund[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([getAllPayments(), getAllRefunds(), getAllTransactions()])
      .then(([p, r, t]) => {
        setPayments(p);
        setRefunds(r);
        setTransactions(t);
      })
      .catch(() => setError("Ne mogu da učitam podatke o plaćanjima. Da li backend radi?"))
      .finally(() => setLoading(false));
  }, []);

  const totalRevenue = payments
    .filter((p) => p.status === "paid")
    .reduce((sum, p) => sum + p.amount, 0);

  const paidCount = payments.filter((p) => p.status === "paid").length;
  const failedCount = payments.filter((p) => p.status === "not_paid").length;
  const refundedCount = payments.filter((p) => p.status === "refunded").length;

  const statusBadge = (status: string) => {
    const colors: Record<string, string> = {
      paid: "bg-green-100 text-green-700",
      success: "bg-green-100 text-green-700",
      pending: "bg-amber-100 text-amber-700",
      not_paid: "bg-red-100 text-red-700",
      failed: "bg-red-100 text-red-700",
      refunded: "bg-blue-100 text-blue-700",
    };
    return colors[status] || "bg-slate-100 text-slate-600";
  };

  if (loading) return <p className="px-6 py-8 text-center text-slate-500">Učitavanje...</p>;
  if (error) return <p className="px-6 py-8 text-center text-red-600">{error}</p>;

  return (
    <div>
      <h1 className="mb-8 text-3xl font-bold text-slate-900">Izveštaji o prodaji</h1>

      <div className="mb-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Ukupan prihod" value={`${totalRevenue.toLocaleString()} RSD`} />
        <StatCard label="Uspešna plaćanja" value={paidCount} />
        <StatCard label="Neuspešna plaćanja" value={failedCount} />
        <StatCard label="Refundirano" value={refundedCount} />
      </div>

      <div className="mb-6 flex gap-2">
        <TabButton label="Plaćanja" active={tab === "payments"} onClick={() => setTab("payments")} />
        <TabButton label="Refundacije" active={tab === "refunds"} onClick={() => setTab("refunds")} />
        <TabButton label="Transakcije" active={tab === "transactions"} onClick={() => setTab("transactions")} />
      </div>

      {tab === "payments" && (
        <div className="overflow-hidden rounded-2xl bg-white shadow-lg">
          <table className="w-full text-left">
            <thead className="bg-slate-50 text-sm text-slate-500">
              <tr>
                <th className="px-6 py-3 font-medium">ID</th>
                <th className="px-6 py-3 font-medium">Korisnik ID</th>
                <th className="px-6 py-3 font-medium">Rezervacija ID</th>
                <th className="px-6 py-3 font-medium">Iznos</th>
                <th className="px-6 py-3 font-medium">Status</th>
                <th className="px-6 py-3 font-medium">Kreirano</th>
              </tr>
            </thead>
            <tbody>
              {payments.map((p) => (
                <tr key={p.id} className="border-t border-slate-100 hover:bg-slate-50">
                  <td className="px-6 py-4 text-slate-700">{p.id}</td>
                  <td className="px-6 py-4 text-slate-700">{p.user_id}</td>
                  <td className="px-6 py-4 text-slate-700">{p.reservation_id}</td>
                  <td className="px-6 py-4 font-medium text-slate-900">{p.amount.toLocaleString()} RSD</td>
                  <td className="px-6 py-4">
                    <span className={`rounded-full px-3 py-1 text-xs font-semibold ${statusBadge(p.status)}`}>
                      {p.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-slate-600">{new Date(p.created_at).toLocaleString("sr-RS")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {tab === "refunds" && (
        <div className="overflow-hidden rounded-2xl bg-white shadow-lg">
          <table className="w-full text-left">
            <thead className="bg-slate-50 text-sm text-slate-500">
              <tr>
                <th className="px-6 py-3 font-medium">ID</th>
                <th className="px-6 py-3 font-medium">Plaćanje ID</th>
                <th className="px-6 py-3 font-medium">Iznos</th>
                <th className="px-6 py-3 font-medium">Status</th>
                <th className="px-6 py-3 font-medium">Datum refundacije</th>
              </tr>
            </thead>
            <tbody>
              {refunds.map((r) => (
                <tr key={r.id} className="border-t border-slate-100 hover:bg-slate-50">
                  <td className="px-6 py-4 text-slate-700">{r.id}</td>
                  <td className="px-6 py-4 text-slate-700">{r.payment_id}</td>
                  <td className="px-6 py-4 font-medium text-slate-900">{r.amount.toLocaleString()} RSD</td>
                  <td className="px-6 py-4">
                    <span className={`rounded-full px-3 py-1 text-xs font-semibold ${statusBadge(r.status)}`}>
                      {r.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-slate-600">
                    {r.refunded_at ? new Date(r.refunded_at).toLocaleString("sr-RS") : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {tab === "transactions" && (
        <div className="overflow-hidden rounded-2xl bg-white shadow-lg">
          <table className="w-full text-left">
            <thead className="bg-slate-50 text-sm text-slate-500">
              <tr>
                <th className="px-6 py-3 font-medium">ID</th>
                <th className="px-6 py-3 font-medium">Plaćanje ID</th>
                <th className="px-6 py-3 font-medium">Iznos</th>
                <th className="px-6 py-3 font-medium">Status</th>
                <th className="px-6 py-3 font-medium">Obrađeno</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((t) => (
                <tr key={t.id} className="border-t border-slate-100 hover:bg-slate-50">
                  <td className="px-6 py-4 text-slate-700">{t.id}</td>
                  <td className="px-6 py-4 text-slate-700">{t.payment_id}</td>
                  <td className="px-6 py-4 font-medium text-slate-900">{t.amount.toLocaleString()} RSD</td>
                  <td className="px-6 py-4">
                    <span className={`rounded-full px-3 py-1 text-xs font-semibold ${statusBadge(t.status)}`}>
                      {t.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-slate-600">
                    {t.processed_at ? new Date(t.processed_at).toLocaleString("sr-RS") : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
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

function StatCard({ label, value }: { label: string; value: number | string }) {
  return (
    <div className="rounded-2xl bg-white p-6 shadow-lg">
      <p className="text-sm text-slate-500">{label}</p>
      <p className="mt-2 text-3xl font-bold text-blue-600">{value}</p>
    </div>
  );
}

export default AdminDashboardPage;