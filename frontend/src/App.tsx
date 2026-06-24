import { Routes, Route } from "react-router-dom";
import EventDetailsPage from "./pages/EventDetailsPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import EventsPage from "./pages/EventsPage";
import UserDashboardPage from "./pages/UserDashboardPage";
import AdminDashboardPage from "./pages/AdminDashboardPage";
import UserProfilePage from "./pages/UserProfilePage";
import ProtectedRoute from "./routes/ProtectedRoute";
import AdminRoute from "./routes/AdminRoute";
import EventsRoute from "./routes/EventsRoute";
import MyTicketsPage from "./pages/MyTicketsPage";
import ReserveTicketPage from "./pages/ReserveTicketPage";

function App() {
  return (
    <Routes>
      <Route path="/" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      <Route
        path="/events"
        element={
          <EventsRoute>
            <EventsPage />
          </EventsRoute>
        }
      />
      <Route path="/events/:eventId/reserve" element={<ReserveTicketPage />} />
      <Route path="/events/:id" element={<EventDetailsPage />} />
      <Route path="/my-tickets" element={<MyTicketsPage />} />
      
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <UserDashboardPage />
          </ProtectedRoute>
        }
      />
      <Route path="/profile" element={<UserProfilePage />} />
      <Route
        path="/admin-dashboard"
        element={
          <AdminRoute>
            <AdminDashboardPage />
          </AdminRoute>
        }
      />
    </Routes>
  );
}

export default App;