import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import logo from "../assets/LOGO.png";

type Seat = {
  id: number;
  event_id: number;
  row_label: string;
  seat_number: number;
  status: string;
};

type Ticket = {
  id: number;
  event_id: number;
  seat_id: number;
  price: number;
  status: string;
};

type EventInfo = {
  id: number;
  title: string;
  description: string;
  start_time: string;
  venue?: {
    name: string;
    city: string;
  };
};

type SeatWithTicket = Seat & {
  ticket_id: number;
  price: number;
  ticket_status: string;
};

function ReserveTicketPage() {
  const { eventId } = useParams();
  const navigate = useNavigate();

  const [event, setEvent] = useState<EventInfo | null>(null);
  const [seats, setSeats] = useState<SeatWithTicket[]>([]);
  const [selectedSeat, setSelectedSeat] = useState<SeatWithTicket | null>(null);
  const [loading, setLoading] = useState(true);
  const [reserving, setReserving] = useState(false);

  const token = localStorage.getItem("token");

  useEffect(() => {
    async function fetchData() {
      try {
        const [eventRes, seatsRes, ticketsRes] = await Promise.all([
          fetch(`http://localhost:8000/api/events/${eventId}`),
          fetch(`http://localhost:8000/api/tickets/event/${eventId}/seats`),
          fetch(`http://localhost:8000/api/tickets/event/${eventId}`),
        ]);

        const eventData = await eventRes.json();
        const seatsData: Seat[] = await seatsRes.json();
        const ticketsData: Ticket[] = await ticketsRes.json();

        const seatsWithTickets = seatsData.map((seat) => {
          const ticket = ticketsData.find((t) => t.seat_id === seat.id);

          return {
            ...seat,
            ticket_id: ticket?.id ?? 0,
            price: ticket?.price ?? 0,
            ticket_status: ticket?.status ?? seat.status,
          };
        });

        setEvent(eventData);
        setSeats(seatsWithTickets);
      } catch (error) {
        console.error("Failed to load reservation page", error);
      } finally {
        setLoading(false);
      }
    }

    fetchData();

    const interval = setInterval(fetchData, 5000);

    return () => clearInterval(interval);

  }, [eventId]);

  const groupedSeats = seats.reduce<Record<string, SeatWithTicket[]>>(
    (groups, seat) => {
      if (!groups[seat.row_label]) {
        groups[seat.row_label] = [];
      }

      groups[seat.row_label].push(seat);
      return groups;
    },
    {}
  );

  Object.values(groupedSeats).forEach((rowSeats) => {
    rowSeats.sort((a, b) => a.seat_number - b.seat_number);
  });

  function getSeatClass(seat: SeatWithTicket) {
    if (selectedSeat?.id === seat.id) {
      return "bg-blue-600 text-white ring-2 ring-blue-300";
    }

    if (seat.ticket_status === "available") {
      return "bg-green-600 hover:bg-green-500 text-white";
    }

    if (seat.ticket_status === "reserved") {
      return "bg-yellow-500 text-slate-950 cursor-not-allowed";
    }

    if (seat.ticket_status === "sold") {
      return "bg-red-600 text-white cursor-not-allowed";
    }

    return "bg-slate-700 text-white";
  }

  async function reserveTicket() {
    if (!selectedSeat) return;

    if (!token) {
      navigate("/");
      return;
    }

    try {
      setReserving(true);

      const response = await fetch("http://localhost:8000/api/tickets/reserve", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          ticket_id: selectedSeat.ticket_id,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to reserve ticket");
      }

      navigate("/my-tickets");
    } catch (error) {
      console.error(error);
      alert("Ticket could not be reserved.");
    } finally {
      setReserving(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 p-8 text-white">
        Loading reservation page...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <header className="flex items-center justify-between px-8 py-6">
        <Link to="/events">
          <img src={logo} alt="ticketGo" className="w-44" />
        </Link>

        <Link
          to="/my-tickets"
          className="rounded-xl bg-blue-600 px-5 py-2 font-semibold hover:bg-blue-500"
        >
          My Tickets
        </Link>
      </header>

      <main className="px-8 py-8">
        <div className="mb-8 rounded-2xl border border-slate-800 bg-slate-900 p-6">
          <h1 className="text-4xl font-bold">{event?.title}</h1>

          <p className="mt-3 text-slate-400">{event?.description}</p>

          <div className="mt-4 text-sm text-slate-300">
            <p>{event && new Date(event.start_time).toLocaleString()}</p>
            {event?.venue && (
              <p>
                {event.venue.name}, {event.venue.city}
              </p>
            )}
          </div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-8">
          <div className="mx-auto mb-8 max-w-xl rounded-xl bg-slate-800 py-3 text-center font-bold tracking-widest text-slate-300">
            STAGE
          </div>

          <div className="space-y-4">
            {Object.entries(groupedSeats).map(([row, rowSeats]) => (
              <div key={row} className="flex items-center gap-4">
                <span className="w-8 text-lg font-bold">{row}</span>

                <div className="flex flex-wrap gap-3">
                  {rowSeats.map((seat) => (
                    <button
                      key={seat.id}
                      disabled={seat.ticket_status !== "available"}
                      onClick={() => setSelectedSeat(seat)}
                      className={`h-11 w-11 rounded-xl font-bold transition ${getSeatClass(
                        seat
                      )}`}
                    >
                      {seat.seat_number}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <div className="mt-8 flex flex-wrap gap-4 text-sm">
            <span className="flex items-center gap-2">
              <span className="h-4 w-4 rounded bg-green-600" /> Available
            </span>
            <span className="flex items-center gap-2">
              <span className="h-4 w-4 rounded bg-yellow-500" /> Reserved
            </span>
            <span className="flex items-center gap-2">
              <span className="h-4 w-4 rounded bg-red-600" /> Sold
            </span>
            <span className="flex items-center gap-2">
              <span className="h-4 w-4 rounded bg-blue-600" /> Selected
            </span>
          </div>
        </div>

        <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-900 p-6">
          {selectedSeat ? (
            <>
              <h2 className="text-2xl font-bold">
                Selected seat: {selectedSeat.row_label}
                {selectedSeat.seat_number}
              </h2>

              <p className="mt-2 text-slate-400">
                Price: {selectedSeat.price} RSD
              </p>

              <button
                onClick={reserveTicket}
                disabled={reserving}
                className="mt-5 rounded-xl bg-blue-600 px-6 py-3 font-semibold hover:bg-blue-500 disabled:opacity-60"
              >
                {reserving ? "Reserving..." : "Reserve Ticket"}
              </button>
            </>
          ) : (
            <p className="text-slate-400">Select an available seat.</p>
          )}
        </div>
      </main>
    </div>
  );
}

export default ReserveTicketPage;