import { Link } from "react-router-dom";
import logo from "../assets/LOGO.png";

function EventsPage() {
  const isGuest = localStorage.getItem("guest") === "true";

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <header className="flex items-center justify-between px-8 py-6">
        <img src={logo} alt="ticketGo" className="w-48" />

        <div>
          {isGuest ? (
            <Link to="/" className="rounded-xl bg-blue-600 px-5 py-2 font-semibold">
              Login
            </Link>
          ) : (
            <Link to="/dashboard" className="rounded-xl bg-blue-600 px-5 py-2 font-semibold">
              My Dashboard
            </Link>
          )}
        </div>
      </header>

      <main className="px-8 py-10">
        <h1 className="text-4xl font-bold">Upcoming Events</h1>
        <p className="mt-2 text-slate-400">
          Discover concerts, festivals and live shows.
        </p>

        <div className="mt-10 grid gap-6 md:grid-cols-3">
          {["Summer Festival", "Rock Night", "Tech Conference"].map((event) => (
            <div key={event} className="rounded-2xl bg-white p-6 text-slate-900">
              <div className="mb-5 h-36 rounded-xl bg-slate-200" />
              <h2 className="text-xl font-bold">{event}</h2>
              <p className="mt-2 text-sm text-slate-500">Belgrade Arena</p>
              <p className="mt-1 text-sm text-slate-500">From 2500 RSD</p>

              <button className="mt-5 w-full rounded-xl bg-blue-600 py-3 font-semibold text-white">
                {isGuest ? "Login to reserve" : "Reserve ticket"}
              </button>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}

export default EventsPage;