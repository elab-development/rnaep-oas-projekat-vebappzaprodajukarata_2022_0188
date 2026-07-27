const API = "http://localhost:8000/api";

export interface PaymentMethod {
  id: number;
  name: string;
}

export interface Payment {
  id: number;
  reservation_id: number;
  user_id: number;
  payment_method_id: number;
  amount: number;
  status: string;
  created_at: string;
  paid_at: string | null;
}

function authHeaders() {
  return { Authorization: `Bearer ${localStorage.getItem("token")}` };
}

export async function getMyTickets() {
  const res = await fetch(`${API}/tickets/my/tickets`, {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error("Ne mogu da učitam karte.");
  return res.json();
}

export async function createPayment(data: {
  reservation_id: number;
  payment_method_id: number;
  amount: number;
  user_email: string;
  event_name: string;
  event_date: string;
  venue_name: string;
  venue_address: string;
}): Promise<Payment> {
  const res = await fetch(`${API}/payments`, {
    method: "POST",
    headers: { ...authHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Greška pri plaćanju.");
  }
  return res.json();
}

export async function confirmOrderPayment(orderId: number, paymentId: number): Promise<void> {
  const res = await fetch(`${API}/tickets/orders/${orderId}/confirm-payment?payment_id=${paymentId}`, {
    method: "POST",
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error("Greška pri potvrdi plaćanja.");
}

export async function failOrderPayment(orderId: number): Promise<void> {
  const res = await fetch(`${API}/tickets/orders/${orderId}/fail-payment`, {
    method: "POST",
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error("Greška pri prijavi neuspelog plaćanja.");
}

export async function cancelReservation(reservationId: number): Promise<void> {
  const res = await fetch(`${API}/tickets/reservations/${reservationId}/cancel`, {
    method: "POST",
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error("Greška pri otkazivanju rezervacije.");
}

export async function getReservation(reservationId: number) {
  const res = await fetch(`${API}/tickets/reservations/${reservationId}`, {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error("Rezervacija nije pronađena.");
  return res.json();
}



