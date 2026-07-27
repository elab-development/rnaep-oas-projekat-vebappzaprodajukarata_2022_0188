export interface Venue {
  id: number;
  name: string;
  address: string;
  city: string;
  capacity: number;
  latitude: number | null;
  longitude: number | null;
}

export interface Category {
  id: number;
  name: string;
  description: string | null;
}

export interface Event {
  id: number;
  title: string;
  description: string | null;
  start_time: string;
  end_time: string;
  status: string;
  venue_id: number;
  category_id: number;
  created_at: string;
  updated_at: string;
  venue: Venue;
  category: Category;
}