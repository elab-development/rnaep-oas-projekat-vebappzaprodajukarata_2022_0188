import { Link } from "react-router-dom";
import logo from "../assets/LOGO.png";
import EventCard from "../components/EventCard";
import { useEffect, useState } from "react";
import type { Event } from "../types/event_service/Event";
import { fetchEvents } from "../services/eventService";

function EventsPage() {
  const isGuest = localStorage.getItem("guest") === "true";

  const [events, setEvents] = useState<Event[]>([]);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  useEffect(() => {
    fetchEvents()
      .then((data) => setEvents(data))
      .catch((error) => console.log(error));
  }, []);

  const filteredEvents = events.filter((event) => {
    const matchesSearch =
      event.title.toLowerCase().includes(search.toLowerCase()) ||
      event.description?.toLowerCase().includes(search.toLowerCase()) ||
      event.venue.name.toLowerCase().includes(search.toLowerCase()) ||
      event.venue.city.toLowerCase().includes(search.toLowerCase()) ||
      event.category.name.toLowerCase().includes(search.toLowerCase());

    const matchesStatus =
      statusFilter === "all" || event.status === statusFilter;

    return matchesSearch && matchesStatus;
  });

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <header className="flex items-center justify-between px-8 py-6 border-b border-slate-800">
        <img src={logo} alt="ticketGo" className="w-48" />

        {isGuest ? (
          <Link to="/" className="rounded-xl bg-blue-600 px-5 py-2 font-semibold hover:bg-blue-700">
            Login
          </Link>
        ) : (
          <Link to="/dashboard" className="rounded-xl bg-blue-600 px-5 py-2 font-semibold hover:bg-blue-700">
            My Dashboard
          </Link>
        )}
      </header>

      <main className="px-8 py-10">
        <div className="flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
          <div>
            <h1 className="text-4xl font-bold">Events</h1>
            <p className="mt-2 text-slate-400">
              Discover concerts, sport events, conferences and theatre shows.
            </p>
          </div>

          <div className="flex flex-col gap-3 md:w-[520px]">
            <input
              type="text"
              placeholder="Search by title, city, venue or category..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-white outline-none focus:border-blue-600"
            />

            <div className="flex flex-wrap gap-3">
              {["all", "scheduled", "finished", "cancelled"].map((status) => (
                <button
                  key={status}
                  onClick={() => setStatusFilter(status)}
                  className={`rounded-xl px-4 py-2 font-semibold transition ${
                    statusFilter === status
                      ? "bg-blue-600 text-white"
                      : "bg-slate-800 text-slate-300 hover:bg-slate-700"
                  }`}
                >
                  {status.charAt(0).toUpperCase() + status.slice(1)}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="mt-10 grid gap-6 md:grid-cols-2 xl:grid-cols-3">
          {filteredEvents.map((event) => (
            <EventCard key={event.id} event={event} />
          ))}
        </div>

        {filteredEvents.length === 0 && (
          <div className="mt-12 rounded-3xl border border-slate-800 bg-slate-900 p-10 text-center">
            <h2 className="text-2xl font-bold">No events found</h2>
            <p className="mt-2 text-slate-400">
              Try changing your search or selected filter.
            </p>
          </div>
        )}
      </main>
    </div>
  );
}

export default EventsPage;