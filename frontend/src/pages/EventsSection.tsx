import { useEffect, useState } from "react";

const API = "http://localhost:8000";

interface Event {
  id: number;
  title: string;
  description: string | null;
  start_time: string;
  end_time: string;
  status: string;
  venue_id: number;
  category_id: number;
}
interface Venue { id: number; name: string; city: string; }
interface Category { id: number; name: string; }

function EventsSection() {
  const [events, setEvents] = useState<Event[]>([]);
  const [venues, setVenues] = useState<Venue[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [formError, setFormError] = useState("");
  const [form, setForm] = useState({
    title: "", description: "", start_time: "", end_time: "",
    venue_id: "", category_id: "",
  });

  const token = localStorage.getItem("token");
  const authHeaders = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
    "X-User-Role": "admin", // Event servis traži ulogu kroz header
  };

  const loadAll = async () => {
    const [evRes, vRes, cRes] = await Promise.all([
      fetch(`${API}/events/`),
      fetch(`${API}/venues/`),
      fetch(`${API}/categories/`),
    ]);
    if (!evRes.ok) throw new Error();
    setEvents(await evRes.json());
    setVenues(vRes.ok ? await vRes.json() : []);
    setCategories(cRes.ok ? await cRes.json() : []);
  };

  useEffect(() => {
    loadAll()
      .catch(() => setError("Ne mogu da učitam događaje. Da li backend radi i da li je CORS sređen?"))
      .finally(() => setLoading(false));
  }, []);

  const handleDelete = async (id: number) => {
    if (!window.confirm("Obrisati ovaj događaj?")) return;
    try {
      const res = await fetch(`${API}/events/${id}`, { method: "DELETE", headers: authHeaders });
      if (!res.ok) throw new Error();
      setEvents(events.filter((e) => e.id !== id));
    } catch {
      window.alert("Greška pri brisanju (možda nemaš admin prava na gateway-u).");
    }
  };

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError("");
    try {
      const res = await fetch(`${API}/events/`, {
        method: "POST",
        headers: authHeaders,
        body: JSON.stringify({
          title: form.title,
          description: form.description || null,
          start_time: form.start_time,
          end_time: form.end_time,
          venue_id: Number(form.venue_id),
          category_id: Number(form.category_id),
        }),
      });
      if (!res.ok) {
        const d = await res.json();
        throw new Error(typeof d.detail === "string" ? d.detail : "Greška pri dodavanju.");
      }
      await loadAll();
      setShowModal(false);
      setForm({ title: "", description: "", start_time: "", end_time: "", venue_id: "", category_id: "" });
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "Greška pri dodavanju događaja.");
    }
  };

  const venueName = (id: number) => venues.find((v) => v.id === id)?.name ?? `#${id}`;
  const fmt = (d: string) => new Date(d).toLocaleString("sr-RS", { dateStyle: "medium", timeStyle: "short" });
  const inputClass = "w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100";

  return (
    <div>
      <h1 className="mb-8 text-3xl font-bold text-slate-900">Upravljanje događajima</h1>

      <div className="overflow-hidden rounded-2xl bg-white shadow-lg">
        <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
          <h2 className="text-lg font-semibold text-slate-900">Lista događaja</h2>
          <button
            onClick={() => setShowModal(true)}
            className="rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700"
          >
            + Dodaj događaj
          </button>
        </div>

        {loading ? (
          <p className="px-6 py-8 text-center text-slate-500">Učitavanje...</p>
        ) : error ? (
          <p className="px-6 py-8 text-center text-red-600">{error}</p>
        ) : events.length === 0 ? (
          <p className="px-6 py-8 text-center text-slate-500">Nema događaja. Dodaj prvi!</p>
        ) : (
          <table className="w-full text-left">
            <thead className="bg-slate-50 text-sm text-slate-500">
              <tr>
                <th className="px-6 py-3 font-medium">ID</th>
                <th className="px-6 py-3 font-medium">Naziv</th>
                <th className="px-6 py-3 font-medium">Početak</th>
                <th className="px-6 py-3 font-medium">Lokacija</th>
                <th className="px-6 py-3 font-medium">Status</th>
                <th className="px-6 py-3 font-medium">Akcije</th>
              </tr>
            </thead>
            <tbody>
              {events.map((ev) => (
                <tr key={ev.id} className="border-t border-slate-100 hover:bg-slate-50">
                  <td className="px-6 py-4 text-slate-700">{ev.id}</td>
                  <td className="px-6 py-4 font-medium text-slate-900">{ev.title}</td>
                  <td className="px-6 py-4 text-slate-600">{fmt(ev.start_time)}</td>
                  <td className="px-6 py-4 text-slate-600">{venueName(ev.venue_id)}</td>
                  <td className="px-6 py-4">
                    <span className={`rounded-full px-3 py-1 text-xs font-semibold ${
                      ev.status === "cancelled" ? "bg-red-100 text-red-700" : "bg-green-100 text-green-700"
                    }`}>
                      {ev.status}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <button
                      onClick={() => handleDelete(ev.id)}
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

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
          <div className="w-full max-w-md rounded-2xl bg-white p-8 shadow-2xl">
            <h2 className="mb-6 text-2xl font-bold text-slate-900">Novi događaj</h2>
            <form onSubmit={handleAdd} className="space-y-4">
              <input className={inputClass} placeholder="Naziv" value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })} required />
              <input className={inputClass} placeholder="Opis (opciono)" value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })} />
              <label className="block text-sm text-slate-500">Početak</label>
              <input className={inputClass} type="datetime-local" value={form.start_time}
                onChange={(e) => setForm({ ...form, start_time: e.target.value })} required />
              <label className="block text-sm text-slate-500">Kraj</label>
              <input className={inputClass} type="datetime-local" value={form.end_time}
                onChange={(e) => setForm({ ...form, end_time: e.target.value })} required />
              <select className={inputClass} value={form.venue_id}
                onChange={(e) => setForm({ ...form, venue_id: e.target.value })} required>
                <option value="">Izaberi lokaciju</option>
                {venues.map((v) => <option key={v.id} value={v.id}>{v.name} ({v.city})</option>)}
              </select>
              <select className={inputClass} value={form.category_id}
                onChange={(e) => setForm({ ...form, category_id: e.target.value })} required>
                <option value="">Izaberi kategoriju</option>
                {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
              {formError && <p className="text-sm text-red-600">{formError}</p>}
              <div className="flex gap-3 pt-2">
                <button type="submit" className="flex-1 rounded-xl bg-blue-600 py-3 font-semibold text-white hover:bg-blue-700">Dodaj</button>
                <button type="button" onClick={() => { setShowModal(false); setFormError(""); }}
                  className="flex-1 rounded-xl border border-slate-300 py-3 font-semibold text-slate-700 hover:bg-slate-100">Otkaži</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default EventsSection;