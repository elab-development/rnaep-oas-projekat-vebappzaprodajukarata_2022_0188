import type { Event } from "../types/event_service/Event";
import { Link } from "react-router-dom";
interface EventCardProps {
  event: Event;
}

function EventCard({ event }: EventCardProps) {
  return (
    <div className="rounded-2xl bg-slate-800 p-5 border border-slate-700">
      <div className="flex items-center justify-between">
        <span className="rounded-full bg-blue-600 px-3 py-1 text-sm">
          {event.category.name}
        </span>

        <span className="text-sm text-slate-400">
          {event.status}
        </span>
      </div>

      <h3 className="mt-4 text-xl font-bold text-white">
        {event.title}
      </h3>

      <p className="mt-2 text-sm text-slate-400">
        {event.description}
      </p>

      <div className="mt-5 space-y-1 text-sm text-slate-300">
        <p>
          {event.venue.name}, {event.venue.city}
        </p>

        <p>
          {new Date(event.start_time).toLocaleString()}
        </p>
      </div>

      <Link
        to={`/events/${event.id}`}
        className="mt-5 block w-full rounded-xl bg-blue-600 py-3 text-center font-semibold text-white hover:bg-blue-700"
      >
        View Details
      </Link>
    </div>
  );
}

export default EventCard;