import { useEffect, useState, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  getMyTickets, createPayment, confirmOrderPayment, failOrderPayment, cancelReservation,
  type PaymentMethod
} from "../services/paymentService";
import { fetchEventById, fetchVenueById } from "../services/eventService";

interface TicketInfo {
  reservation_id: number;
  order_id: number;
  ticket_id: number;
  event_id: number;
  seat_id: number;
  row_label: string;
  seat_number: number;
  price: number;
  ticket_status: string;
  reservation_status: string;
  order_status: string;
  expires_at: string;
  created_at: string;
}

const PAYMENT_METHODS: PaymentMethod[] = [
  { id: 1, name: "Kreditna kartica" },
  { id: 2, name: "PayPal" },
];

function PaymentPage() {
  const { reservationId } = useParams<{ reservationId: string }>();
  const navigate = useNavigate();

  const [ticket, setTicket] = useState<TicketInfo | null>(null);
  const [eventName, setEventName] = useState("");
  const [eventDate, setEventDate] = useState("");
  const [venueName, setVenueName] = useState("");
  const [venueAddress, setVenueAddress] = useState("");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [paymentMethodId, setPaymentMethodId] = useState<number>(1);
  const [processing, setProcessing] = useState(false);

  const [secondsLeft, setSecondsLeft] = useState<number | null>(null);
  const [expired, setExpired] = useState(false);
  const paymentInProgress = useRef(false);


  useEffect(() => {
    const load = async () => {
      const tickets: TicketInfo[] = await getMyTickets();
      const found = tickets.find((t) => t.reservation_id === Number(reservationId));

      if (!found) {
        setError("Rezervacija nije pronađena.");
        return;
      }
      if (found.reservation_status !== "active") {
        setError("Ova rezervacija nije više aktivna.");
        return;
      }

      setTicket(found);

      const event = await fetchEventById(found.event_id);
      setEventName(event.title);
      setEventDate(event.start_time);

      const venue = await fetchVenueById(event.venue_id);
      setVenueName(venue.name);
      setVenueAddress(`${venue.address}, ${venue.city}`);
    };

    load()
      .catch(() => setError("Greška pri učitavanju podataka o rezervaciji."))
      .finally(() => setLoading(false));
  }, [reservationId]);

  useEffect(() => {
    if (!ticket) return;

    const tick = () => {
      const expiresAtStr = ticket.expires_at.endsWith("Z") ? ticket.expires_at : `${ticket.expires_at}Z`;
      const expiresAt = new Date(expiresAtStr).getTime();
      const now = Date.now();
      const diff = Math.max(0, Math.floor((expiresAt - now) / 1000));
      setSecondsLeft(diff);
      if (diff <= 0) {
        setExpired(true);
      }
    };

    tick();
    const interval = setInterval(tick, 1000);
    return () => clearInterval(interval);
  }, [ticket]);

  const formatTime = (s: number) => {
    const m = Math.floor(s / 60);
    const sec = s % 60;
    return `${m}:${sec.toString().padStart(2, "0")}`;
  };

  const userEmail = localStorage.getItem("email") || "";

  const handlePay = async () => {
  if (!ticket || paymentInProgress.current) return;
  console.log("PAYMENT METHOD ID U TRENUTKU KLIKA:", paymentMethodId);
  paymentInProgress.current = true;
  setProcessing(true);
  setError("");

    try {
      const payment = await createPayment({
        reservation_id: ticket.reservation_id,
        payment_method_id: paymentMethodId,
        amount: ticket.price,
        user_email: userEmail,
        event_name: eventName,
        event_date: eventDate,
        venue_name: venueName,
        venue_address: venueAddress,
      });
      
      if (payment.status === "paid") {
        await confirmOrderPayment(ticket.order_id, payment.id);
        navigate("/my-tickets");
      } else {
        await failOrderPayment(ticket.order_id);
        setError("Plaćanje nije uspelo. Sedište je oslobođeno, možete pokušati ponovo.");
        setTimeout(() => navigate("/events"), 2500);
      }
    } catch {
      if (ticket) await failOrderPayment(ticket.order_id).catch(() => {});
      setError("Greška pri obradi plaćanja.");
    } finally {
      setProcessing(false);
      paymentInProgress.current = false;
    }
  };

  const handleCancel = async () => {
    if (!ticket) return;
    if (!window.confirm("Otkazati rezervaciju?")) return;
    try {
      await cancelReservation(ticket.reservation_id);
      navigate("/events");
    } catch {
      setError("Greška pri otkazivanju rezervacije.");
    }
  };

  if (loading) {
    return <div className="flex min-h-screen items-center justify-center">Učitavanje...</div>;
  }

  if (error && !ticket) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  if (expired) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
        <div className="w-full max-w-md rounded-2xl bg-white p-8 text-center shadow-lg">
          <h2 className="mb-4 text-2xl font-bold text-red-600">Rezervacija je istekla</h2>
          <p className="mb-6 text-slate-600">Vreme za plaćanje je prošlo. Sedište je ponovo dostupno.</p>
          <button onClick={() => navigate("/events")} className="rounded-xl bg-blue-600 px-6 py-3 font-semibold text-white hover:bg-blue-700">
            Nazad na događaje
          </button>
        </div>
      </div>
    );
  }

  if (!ticket) return null;

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-lg rounded-2xl bg-white p-8 shadow-lg">
        <div className="mb-6 flex items-center justify-between">
          <h1 className="text-2xl font-bold text-slate-900">Plaćanje</h1>
          {secondsLeft !== null && (
            <span className={`rounded-full px-4 py-2 text-sm font-semibold ${
              secondsLeft < 60 ? "bg-red-100 text-red-700" : "bg-amber-100 text-amber-700"
            }`}>
              Preostalo: {formatTime(secondsLeft)}
            </span>
          )}
        </div>

        <div className="mb-6 rounded-xl bg-slate-50 p-4">
          <p className="font-semibold text-slate-900">{eventName}</p>
          <p className="text-sm text-slate-600">{new Date(eventDate).toLocaleString("sr-RS")}</p>
          <p className="text-sm text-slate-600">{venueName}, {venueAddress}</p>
          <p className="mt-2 text-sm text-slate-700">
            Sedište: Red {ticket.row_label}, mesto {ticket.seat_number}
          </p>
          <p className="mt-2 text-lg font-bold text-blue-600">{ticket.price.toLocaleString()} RSD</p>
        </div>

        <div className="mb-6">
          <label className="mb-2 block text-sm font-medium text-slate-700">Način plaćanja</label>
          <div className="space-y-2">
            {PAYMENT_METHODS.map((pm) => (
              <label key={pm.id} className="flex items-center gap-3 rounded-xl border border-slate-300 px-4 py-3 cursor-pointer hover:bg-slate-50">
                <input
                  type="radio"
                  name="paymentMethod"
                  checked={paymentMethodId === pm.id}
                  onChange={() => setPaymentMethodId(pm.id)}
                />
                <span className="text-slate-700">{pm.name}</span>
              </label>
            ))}
          </div>
        </div>

        {error && <p className="mb-4 text-sm text-red-600">{error}</p>}

        <div className="flex gap-3">
          <button
            onClick={handlePay}
            disabled={processing}
            className="flex-1 rounded-xl bg-blue-600 py-3 font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {processing ? "Obrada..." : "Plati"}
          </button>
          <button
            onClick={handleCancel}
            disabled={processing}
            className="flex-1 rounded-xl border border-slate-300 py-3 font-semibold text-slate-700 hover:bg-slate-100"
          >
            Otkaži
          </button>
        </div>
      </div>
    </div>
  );
}

export default PaymentPage;