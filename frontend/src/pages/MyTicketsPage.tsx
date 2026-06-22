import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import logo from "../assets/LOGO.png";

type MyTicket = {
  reservation_id: number;
  order_id: number | null;
  ticket_id: number;
  event_id: number;
  seat_id: number | null;
  row_label: string | null;
  seat_number: number | null;
  price: number;
  ticket_status: string;
  reservation_status: string;
  order_status: string | null;
  expires_at: string;
  created_at: string;
  paid_at: string | null;
};

type EventInfo = {
  id: number;
  title: string;
  start_time: string;
  venue?: {
    name: string;
    city: string;
  };
};

function MyTicketsPage() {
  const [tickets, setTickets] = useState<MyTicket[]>([]);
  const [events, setEvents] = useState<Record<number, EventInfo>>({});
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("all");

  const token = localStorage.getItem("token");

  useEffect(() => {
    async function fetchTickets() {
      try {
        const response = await fetch("http://localhost:8000/api/tickets/my/tickets", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error("Failed to fetch tickets");
        }

        const data: MyTicket[] = await response.json();
        setTickets(data);

        const uniqueEventIds = [...new Set(data.map((ticket) => ticket.event_id))];

        const eventResults = await Promise.all(
          uniqueEventIds.map(async (eventId) => {
            const eventResponse = await fetch(
              `http://localhost:8000/api/events/${eventId}`
            );

            if (!eventResponse.ok) return null;

            return eventResponse.json();
          })
        );

        const eventMap: Record<number, EventInfo> = {};

        eventResults.forEach((event) => {
          if (event) {
            eventMap[event.id] = event;
          }
        });

        setEvents(eventMap);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    }

    fetchTickets();
  }, [token]);

  const filteredTickets =
    statusFilter === "all"
      ? tickets
      : tickets.filter((ticket) => ticket.reservation_status === statusFilter);

  function getStatusText(ticket: MyTicket) {
    if (ticket.reservation_status === "active") return "Reserved";
    if (ticket.reservation_status === "confirmed" && ticket.order_status === "paid")
      return "Purchased";
    if (ticket.reservation_status === "expired") return "Expired";
    if (ticket.reservation_status === "cancelled") return "Cancelled";

    return ticket.reservation_status;
  }

  function getStatusClass(ticket: MyTicket) {
    if (ticket.reservation_status === "active")
      return "bg-yellow-500/20 text-yellow-300";
    if (ticket.reservation_status === "confirmed")
      return "bg-green-500/20 text-green-300";
    if (ticket.reservation_status === "expired")
      return "bg-red-500/20 text-red-300";
    if (ticket.reservation_status === "cancelled")
      return "bg-slate-500/20 text-slate-300";

    return "bg-blue-500/20 text-blue-300";
  }

  async function cancelReservation(reservationId: number) {
    try {
      const response = await fetch(
        `http://localhost:8000/api/tickets/reservations/${reservationId}/cancel`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error("Failed to cancel reservation");
      }

      setTickets((prev) =>
        prev.map((ticket) =>
          ticket.reservation_id === reservationId
            ? {
                ...ticket,
                reservation_status: "cancelled",
                ticket_status: "available",
                order_status: "cancelled",
              }
            : ticket
        )
      );
    } catch (error) {
      console.error(error);
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <header className="flex items-center justify-between px-8 py-6">
        <Link to="/dashboard">
          <img src={logo} alt="ticketGo" className="w-44" />
        </Link>

        <Link
          to="/dashboard"
          className="rounded-xl bg-blue-600 px-5 py-2 font-semibold hover:bg-blue-500"
        >
          Dashboard
        </Link>
      </header>

      <main className="px-8 py-8">
        <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <h1 className="text-4xl font-bold">My Tickets</h1>
            <p className="mt-2 text-slate-400">
              View your reservations and purchased tickets.
            </p>
          </div>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-white outline-none"
          >
            <option value="all">All tickets</option>
            <option value="active">Reserved</option>
            <option value="confirmed">Purchased</option>
            <option value="expired">Expired</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>

        {loading ? (
          <p className="text-slate-400">Loading tickets...</p>
        ) : filteredTickets.length === 0 ? (
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-8">
            <h2 className="text-2xl font-semibold">No tickets found</h2>
            <p className="mt-2 text-slate-400">
              Try another filter or browse events.
            </p>

            <Link
              to="/events"
              className="mt-5 inline-block rounded-xl bg-blue-600 px-5 py-3 font-semibold hover:bg-blue-500"
            >
              Browse Events
            </Link>
          </div>
        ) : (
          <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
            {filteredTickets.map((ticket) => {
              const event = events[ticket.event_id];

              return (
                <div
                  key={ticket.reservation_id}
                  className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-lg"
                >
                  <div className="mb-4 flex items-start justify-between gap-3">
                    <div>
                      <h2 className="text-xl font-bold">
                        {event?.title || `Event #${ticket.event_id}`}
                      </h2>

                      <p className="mt-1 text-sm text-slate-400">
                        {event
                          ? `${new Date(event.start_time).toLocaleString()}`
                          : "Event details unavailable"}
                      </p>
                    </div>

                    <span
                      className={`rounded-full px-3 py-1 text-xs font-semibold ${getStatusClass(
                        ticket
                      )}`}
                    >
                      {getStatusText(ticket)}
                    </span>
                  </div>

                  <div className="space-y-2 text-sm text-slate-300">
                    {event?.venue && (
                      <p>
                        <span className="text-slate-500">Venue:</span>{" "}
                        {event.venue.name}, {event.venue.city}
                      </p>
                    )}

                    <p>
                      <span className="text-slate-500">Seat:</span>{" "}
                      {ticket.row_label}
                      {ticket.seat_number}
                    </p>

                    <p>
                      <span className="text-slate-500">Price:</span>{" "}
                      {ticket.price} RSD
                    </p>

                    {ticket.reservation_status === "active" && (
                      <p>
                        <span className="text-slate-500">Reserved until:</span>{" "}
                        {new Date(ticket.expires_at).toLocaleString()}
                      </p>
                    )}

                    {ticket.paid_at && (
                      <p>
                        <span className="text-slate-500">Paid at:</span>{" "}
                        {new Date(ticket.paid_at).toLocaleString()}
                      </p>
                    )}
                  </div>

                  {ticket.reservation_status === "active" && (
                    <div className="mt-6 flex gap-3">
                      <button className="flex-1 rounded-xl bg-blue-600 px-4 py-2 font-semibold hover:bg-blue-500">
                        Pay Now
                      </button>

                      <button
                        onClick={() => cancelReservation(ticket.reservation_id)}
                        className="flex-1 rounded-xl bg-red-600 px-4 py-2 font-semibold hover:bg-red-500"
                      >
                        Cancel
                      </button>
                    </div>
                  )}

                  {ticket.reservation_status === "confirmed" && (
                    <button className="mt-6 w-full rounded-xl bg-green-600 px-4 py-2 font-semibold hover:bg-green-500">
                      View QR Ticket
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
}

export default MyTicketsPage;