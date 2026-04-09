import { useState, useEffect } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { motion } from "framer-motion";
import { Gift, Mail, Lock, User, ArrowRight, Loader2 } from "lucide-react";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import { register, clearError } from "../store/authSlice";
import { Sparkles } from "../components/Sparkles";

export default function RegisterPage() {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const redirect = searchParams.get("redirect") || "/";
  const { loading, error, token } = useAppSelector((s) => s.auth);

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  useEffect(() => {
    if (token) navigate(redirect, { replace: true });
    return () => { dispatch(clearError()); };
  }, [token]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await dispatch(register({ name, email, password }));
    if (res.meta.requestStatus === "fulfilled") navigate(redirect, { replace: true });
  };

  return (
    <div className="page-bg flex items-center justify-center min-h-screen p-4 relative overflow-hidden">
      <Sparkles />

      <motion.div
        initial={{ opacity: 0, y: 30, scale: 0.96 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ type: "spring", stiffness: 300, damping: 25 }}
        className="glass-card rounded-3xl p-8 w-full max-w-sm z-10"
      >
        <div className="flex flex-col items-center mb-8">
          <motion.div
            animate={{ scale: [1, 1.1, 1] }}
            transition={{ duration: 1.5, repeat: Infinity, repeatDelay: 2 }}
            className="w-16 h-16 rounded-2xl bg-gradient-to-br from-pink-500 to-rose-500 flex items-center justify-center shadow-xl shadow-rose-200 mb-4"
          >
            <Gift className="w-8 h-8 text-white" />
          </motion.div>
          <h1 className="text-2xl font-bold gradient-text">Создать аккаунт</h1>
          <p className="text-sm text-gray-500 mt-1">Начните делиться желаниями</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="relative">
            <User className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              className="input-field pl-10"
              placeholder="Ваше имя"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>
          <div className="relative">
            <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              className="input-field pl-10"
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="relative">
            <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              className="input-field pl-10"
              type="password"
              placeholder="Пароль (мин. 8 символов)"
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          {error && (
            <motion.p
              initial={{ opacity: 0, y: -4 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-sm text-rose-500 text-center bg-rose-50 px-3 py-2 rounded-xl"
            >
              {error}
            </motion.p>
          )}

          <motion.button
            type="submit"
            disabled={loading}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="btn-primary w-full justify-center py-3 mt-2"
          >
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <>Зарегистрироваться <ArrowRight className="w-4 h-4" /></>
            )}
          </motion.button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-6">
          Уже есть аккаунт?{" "}
          <Link
            to={redirect !== "/" ? `/login?redirect=${encodeURIComponent(redirect)}` : "/login"}
            className="text-purple-600 font-semibold hover:text-purple-700"
          >
            Войти
          </Link>
        </p>
      </motion.div>
    </div>
  );
}
