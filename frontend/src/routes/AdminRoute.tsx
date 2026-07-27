import { Navigate } from "react-router-dom";
import { isAuthenticated, isAdmin } from "../utils/auth";

interface AdminRouteProps {
  children: React.ReactNode;
}

function AdminRoute({ children }: AdminRouteProps) {
  if (!isAuthenticated()) {
    return <Navigate to="/" replace />;
  }

  if (!isAdmin()) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}

export default AdminRoute;