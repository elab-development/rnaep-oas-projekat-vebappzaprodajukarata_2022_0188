import { Link, useNavigate, useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import logo from "../assets/LOGO.png";
import type { Event } from "../types/event_service/Event";
import { fetchEvents } from "../services/eventService";

function EventDetailsPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isGuest = localStorage.getItem("guest") === "true";

  const [event, setEvent] = useState<Event | null>(null);

  useEffect(() => {
    fetchEvents()
      .then((data) => {
        const foundEvent = data.find((event) => event.id === Number(id));
        setEvent(foundEvent || null);
      })
      .catch((error) => console.log(error));
  }, [id]);

  if (!event) {
    return (
      <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center">
        <p className="text-slate-400">Event not found.</p>
      </div>
    );
  }

  const handleReserve = () => {
    if (isGuest) {
      navigate("/");
      return;
    }

    navigate(`/events/${event.id}/reserve`);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <header className="flex items-center justify-between px-8 py-6 border-b border-slate-800">
        <img src={logo} alt="ticketGo" className="w-48" />

        <Link
          to="/events"
          className="rounded-xl bg-slate-800 px-5 py-2 font-semibold hover:bg-slate-700"
        >
          Back to events
        </Link>
      </header>

      <main className="mx-auto max-w-6xl px-8 py-10">
        <span className="rounded-full bg-blue-600 px-4 py-2 text-sm font-semibold">
          {event.category.name}
        </span>

        <h1 className="mt-6 text-5xl font-bold">{event.title}</h1>

        <p className="mt-4 max-w-3xl text-slate-400">
          {event.description}
        </p>

        <div className="mt-10 grid gap-6 md:grid-cols-2">
          <div className="rounded-3xl border border-slate-800 bg-slate-900 p-6">
            <h2 className="text-2xl font-bold">Event info</h2>

            <div className="mt-5 space-y-3 text-slate-300">
              <p><b>Status:</b> {event.status}</p>
              <p><b>Starts:</b> {new Date(event.start_time).toLocaleString()}</p>
              <p><b>Ends:</b> {new Date(event.end_time).toLocaleString()}</p>
              <p><b>Category:</b> {event.category.name}</p>
            </div>
          </div>

          <div className="rounded-3xl border border-slate-800 bg-slate-900 p-6">
            <h2 className="text-2xl font-bold">Venue</h2>

            <div className="mt-5 space-y-3 text-slate-300">
              <p><b>Name:</b> {event.venue.name}</p>
              <p><b>Address:</b> {event.venue.address}</p>
              <p><b>City:</b> {event.venue.city}</p>
              <p><b>Capacity:</b> {event.venue.capacity}</p>
            </div>
          </div>
        </div>

        <button
          onClick={handleReserve}
          className="mt-10 rounded-xl bg-blue-600 px-8 py-4 font-semibold text-white hover:bg-blue-700"
        >
          {isGuest ? "Login to reserve" : "Reserve ticket"}
        </button>
      </main>
    </div>
  );
}

export default EventDetailsPage;