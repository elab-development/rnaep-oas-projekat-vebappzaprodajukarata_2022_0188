import type { Event } from "../types/event_service/Event";

const API_BASE_URL = "http://localhost:8000";

export async function fetchEvents(): Promise<Event[]> {
  const response = await fetch(`${API_BASE_URL}/api/events/`);

  if (!response.ok) {
    throw new Error("Failed to fetch events");
  }

  return response.json();
}

export async function fetchEventById(eventId: number): Promise<Event> {
  const response = await fetch(`${API_BASE_URL}/api/events/${eventId}`);

  if (!response.ok) {
    throw new Error("Failed to fetch event");
  }

  return response.json();
}

export interface Venue {
  id: number;
  name: string;
  address: string;
  city: string;
  capacity: number;
}

export async function fetchVenueById(venueId: number): Promise<Venue> {
  const token = localStorage.getItem("token");
  const response = await fetch(`${API_BASE_URL}/api/venues/${venueId}`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!response.ok) {
    throw new Error("Failed to fetch venue");
  }

  return response.json();
}