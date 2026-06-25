import { Navigate } from "react-router-dom";
import { isAuthenticated, isAdmin } from "../utils/auth";

interface ProtectedRouteProps {
  children: React.ReactNode;
}

function ProtectedRoute({ children }: ProtectedRouteProps) {
  if (!isAuthenticated()) {
    return <Navigate to="/" replace />;
  }

  if (isAdmin()) {
    return <Navigate to="/admin-dashboard" replace />;
  }

  return children;
}

export default ProtectedRoute;