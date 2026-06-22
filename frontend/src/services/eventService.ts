import type { Event } from "../types/event_service/Event";

const API_BASE_URL = "http://localhost:8000";

export async function fetchEvents(): Promise<Event[]> {
  const response = await fetch(`${API_BASE_URL}/api/events/`);

  if (!response.ok) {
    throw new Error("Failed to fetch events");
  }

  return response.json();
}