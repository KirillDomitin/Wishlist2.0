import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Gift, Bookmark, LogOut, Sparkles, User, ShieldCheck } from "lucide-react";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import { logout } from "../store/authSlice";

export function Navbar() {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const name = useAppSelector((s) => s.auth.name);
  const isAdmin = useAppSelector((s) => s.auth.isAdmin);

  const handleLogout = () => {
    dispatch(logout());
    navigate("/login");
  };

  return (
    <motion.nav
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="sticky top-0 z-30 glass-card border-b border-white/60 backdrop-blur-md"
    >
      <div className="max-w-5xl mx-auto px-4 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center shadow-md">
            <Gift className="w-4 h-4 text-white" />
          </div>
          <span className="font-bold text-lg gradient-text">Wishlist</span>
        </Link>

        <div className="flex items-center gap-1">
          <Link to="/" className="btn-ghost">
            <Sparkles className="w-4 h-4" />
            <span className="hidden sm:inline">Мои списки</span>
          </Link>
          <Link to="/reservations" className="btn-ghost">
            <Bookmark className="w-4 h-4" />
            <span className="hidden sm:inline">Бронирования</span>
          </Link>
          {isAdmin && (
            <Link to="/admin" className="btn-ghost text-purple-600 hover:text-purple-700 hover:bg-purple-50">
              <ShieldCheck className="w-4 h-4" />
              <span className="hidden sm:inline">Админ</span>
            </Link>
          )}
          {name && (
            <Link to="/profile" className="hidden sm:flex items-center gap-1.5 text-sm text-gray-600 font-medium px-3 rounded-xl hover:bg-white/60 hover:text-purple-700 transition-all duration-200">
              <User className="w-4 h-4 text-purple-400" />
              {name}
            </Link>
          )}
          <button onClick={handleLogout} className="btn-ghost text-rose-500 hover:text-rose-600 hover:bg-rose-50">
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </motion.nav>
  );
}
