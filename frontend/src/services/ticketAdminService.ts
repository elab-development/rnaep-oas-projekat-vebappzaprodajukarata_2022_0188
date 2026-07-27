const API = "http://localhost:8000/api";

export interface AdminSeat {
  id: number;
  event_id: number;
  row_label: string;
  seat_number: number;
  status: string;
}

export interface AdminTicket {
  id: number;
  event_id: number;
  seat_id: number;
  price: number;
  status: string;
}

function authHeaders() {
  return { Authorization: `Bearer ${localStorage.getItem("token")}` };
}

export async function getTicketsByEvent(eventId: number): Promise<AdminTicket[]> {
  const res = await fetch(`${API}/tickets/event/${eventId}`, { headers: authHeaders() });
  if (!res.ok) throw new Error("Ne mogu da učitam karte za ovaj događaj.");
  return res.json();
}

export async function getSeatsByEvent(eventId: number): Promise<AdminSeat[]> {
  const res = await fetch(`${API}/tickets/event/${eventId}/seats`, { headers: authHeaders() });
  if (!res.ok) throw new Error("Ne mogu da učitam sedišta za ovaj događaj.");
  return res.json();
}

export async function createSeatWithTicket(data: {
  event_id: number;
  row_label: string;
  seat_number: number;
  price: number;
}): Promise<{ message: string; seat: AdminSeat; ticket: AdminTicket }> {
  const res = await fetch(`${API}/tickets/seats`, {
    method: "POST",
    headers: { ...authHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const data = await res.json();
    throw new Error(data.detail || "Greška pri kreiranju sedišta.");
  }
  return res.json();
}