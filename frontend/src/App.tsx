import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { useEffect } from "react";
import { useAppDispatch, useAppSelector } from "./store/hooks";
import { fetchMe } from "./store/authSlice";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import DashboardPage from "./pages/DashboardPage";
import WishlistDetailPage from "./pages/WishlistDetailPage";
import SharedWishlistPage from "./pages/SharedWishlistPage";
import MyReservationsPage from "./pages/MyReservationsPage";
import { Toaster } from "./components/ui/Toaster";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = useAppSelector((s) => s.auth.token);
  return token ? <>{children}</> : <Navigate to="/login" replace />;
}

function AppRoutes() {
  const dispatch = useAppDispatch();
  const token = useAppSelector((s) => s.auth.token);

  useEffect(() => {
    if (token) dispatch(fetchMe());
  }, [token]);
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/shared/:token" element={<SharedWishlistPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/wishlists/:id"
        element={
          <ProtectedRoute>
            <WishlistDetailPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/reservations"
        element={
          <ProtectedRoute>
            <MyReservationsPage />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Toaster>
        <AppRoutes />
      </Toaster>
    </BrowserRouter>
  );
}
