const API = "http://localhost:8000/api";

export interface Venue {
  id: number;
  name: string;
  address: string;
  city: string;
  capacity: number;
  latitude?: number;
  longitude?: number;
}

export interface Category {
  id: number;
  name: string;
  description?: string;
}

export interface AdminEvent {
  id: number;
  title: string;
  description?: string;
  start_time: string;
  end_time: string;
  status: string;
  venue_id: number;
  category_id: number;
  created_at: string;
  updated_at: string;
}

function getToken() {
  return localStorage.getItem("token");
}

function authHeaders() {
  return { Authorization: `Bearer ${getToken()}` };
}

// ---------------- EVENTS ----------------

export async function getAllEvents(): Promise<AdminEvent[]> {
  const res = await fetch(`${API}/events`, { headers: authHeaders() });
  if (!res.ok) throw new Error("Ne mogu da učitam događaje.");
  return res.json();
}

export async function createEvent(data: {
  title: string;
  description?: string;
  start_time: string;
  end_time: string;
  venue_id: number;
  category_id: number;
}): Promise<AdminEvent> {
  const res = await fetch(`${API}/events`, {
    method: "POST",
    headers: { ...authHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Greška pri kreiranju događaja.");
  return res.json();
}

export async function updateEvent(id: number, data: {
  title: string;
  description?: string;
  start_time: string;
  end_time: string;
  venue_id: number;
  category_id: number;
}): Promise<AdminEvent> {
  const res = await fetch(`${API}/events/${id}`, {
    method: "PUT",
    headers: { ...authHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Greška pri izmeni događaja.");
  return res.json();
}

export async function deleteEvent(id: number): Promise<void> {
  const res = await fetch(`${API}/events/${id}`, {
    method: "DELETE",
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error("Greška pri brisanju događaja.");
}

export async function cancelEvent(id: number): Promise<AdminEvent> {
  const res = await fetch(`${API}/events/${id}/cancel`, {
    method: "PATCH",
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error("Greška pri otkazivanju događaja.");
  return res.json();
}

// ---------------- VENUES ----------------

export async function getAllVenues(): Promise<Venue[]> {
  const res = await fetch(`${API}/venues`, { headers: authHeaders() });
  if (!res.ok) throw new Error("Ne mogu da učitam lokacije.");
  return res.json();
}

export async function createVenue(data: {
  name: string;
  address: string;
  city: string;
  capacity: number;
}): Promise<Venue> {
  const res = await fetch(`${API}/venues`, {
    method: "POST",
    headers: { ...authHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Greška pri kreiranju lokacije.");
  return res.json();
}

export async function deleteVenue(id: number): Promise<void> {
  const res = await fetch(`${API}/venues/${id}`, {
    method: "DELETE",
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error("Greška pri brisanju lokacije.");
}

// ---------------- CATEGORIES ----------------

export async function getAllCategories(): Promise<Category[]> {
  const res = await fetch(`${API}/categories`, { headers: authHeaders() });
  if (!res.ok) throw new Error("Ne mogu da učitam kategorije.");
  return res.json();
}

export async function createCategory(data: {
  name: string;
  description?: string;
}): Promise<Category> {
  const res = await fetch(`${API}/categories`, {
    method: "POST",
    headers: { ...authHeaders(), "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Greška pri kreiranju kategorije.");
  return res.json();
}

export async function deleteCategory(id: number): Promise<void> {
  const res = await fetch(`${API}/categories/${id}`, {
    method: "DELETE",
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error("Greška pri brisanju kategorije.");
}