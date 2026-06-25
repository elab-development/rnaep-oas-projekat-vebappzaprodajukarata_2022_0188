import { Link, useNavigate } from "react-router-dom";
import logo from "../assets/LOGO.png";
import EventCard from "../components/EventCard";
import { useEffect, useState } from "react";
import type { Event } from "../types/event_service/Event";
import { fetchEvents } from "../services/eventService";

function UserDashboardPage() {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("user") || "{}");

  const [events, setEvents] = useState<Event[]>([]);
  const scheduledEvents = events.filter((event) => event.status === "scheduled");

  useEffect(() => {
    fetchEvents()
      .then((data) => setEvents(data))
      .catch((error) => console.log(error));
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    localStorage.removeItem("guest");
    navigate("/");
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <header className="flex items-center justify-between px-8 py-5 border-b border-slate-800">
        <img src={logo} alt="ticketGo" className="h-20 w-auto" />

        <button
          onClick={handleLogout}
          className="rounded-xl bg-red-600 px-5 py-2 font-semibold hover:bg-red-700"
        >
          Logout
        </button>
      </header>

      <main className="px-8 py-10">
        <h1 className="text-4xl font-bold">
          Welcome{user?.name ? `, ${user.name}` : ""} 👋
        </h1>

        <p className="mt-3 text-slate-400">
          Discover events, reserve tickets, and manage your profile.
        </p>

        <div className="mt-10 grid gap-6 md:grid-cols-3">
          <Link
            to="/events"
            className="rounded-3xl bg-white p-6 text-slate-900 shadow-xl hover:scale-[1.02] transition"
          >
            <h2 className="text-2xl font-bold">Events</h2>
            <p className="mt-2 text-slate-500">
              Browse available events and venues.
            </p>
          </Link>

          <Link
            to="/my-tickets"
            className="rounded-3xl bg-white p-6 text-slate-900 shadow-xl hover:scale-[1.02] transition"
          >
            <h2 className="text-2xl font-bold">My Tickets</h2>
            <p className="mt-2 text-slate-500">
              View your reservations and purchased tickets.
            </p>
          </Link>

          <Link
            to="/profile"
            className="rounded-3xl bg-white p-6 text-slate-900 shadow-xl hover:scale-[1.02] transition"
          >
            <h2 className="text-2xl font-bold">Profile</h2>
            <p className="mt-2 text-slate-500">
              Manage your account information.
            </p>
          </Link>
        </div>

        <section className="mt-12 rounded-3xl bg-slate-900 p-6 border border-slate-800">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold">Upcoming events</h2>

            <Link
              to="/events"
              className="rounded-xl bg-blue-600 px-5 py-2 font-semibold hover:bg-blue-700"
            >
              Browse events
            </Link>
          </div>

          <div className="mt-6 grid gap-6 md:grid-cols-2 xl:grid-cols-3">
            {scheduledEvents.map((event) => (
              <EventCard key={event.id} event={event} />
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}

export default UserDashboardPage;
