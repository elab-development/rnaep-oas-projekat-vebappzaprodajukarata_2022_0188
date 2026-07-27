import { Navigate } from "react-router-dom";
import { isAuthenticated, isAdmin, isGuest } from "../utils/auth";

interface EventsRouteProps {
  children: React.ReactNode;
}

function EventsRoute({ children }: EventsRouteProps) {
  if (isAdmin()) {
    return <Navigate to="/admin-dashboard" replace />;
  }

  if (!isGuest() && !isAuthenticated()) {
    return <Navigate to="/" replace />;
  }

  return children;
}

export default EventsRoute;