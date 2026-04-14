import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { motion } from "framer-motion";
import { Gift, Lock, ArrowRight, Loader2, CheckCircle2, AlertCircle } from "lucide-react";
import { authApi } from "../api/auth";
import { Sparkles } from "../components/Sparkles";

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") ?? "";
  const navigate = useNavigate();

  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirm) {
      setError("Пароли не совпадают");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      await authApi.resetPassword(token, password);
      setDone(true);
      setTimeout(() => navigate("/login"), 2500);
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } }).response?.data?.detail;
      setError(detail ?? "Ссылка недействительна или истекла.");
    } finally {
      setLoading(false);
    }
  };

  if (!token) {
    return (
      <div className="page-bg flex items-center justify-center min-h-screen p-4">
        <div className="glass-card rounded-3xl p-8 w-full max-w-sm text-center">
          <AlertCircle className="w-12 h-12 text-rose-400 mx-auto mb-3" />
          <p className="text-gray-700 font-medium">Ссылка недействительна</p>
          <Link to="/forgot-password" className="text-purple-600 font-semibold hover:text-purple-700 text-sm mt-4 block">
            Запросить новую ссылку
          </Link>
        </div>
      </div>
    );
  }

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
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center shadow-xl shadow-purple-200 mb-4">
            <Gift className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold gradient-text">Новый пароль</h1>
          <p className="text-sm text-gray-500 mt-1">Придумайте надёжный пароль</p>
        </div>

        {done ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex flex-col items-center gap-3 py-4"
          >
            <CheckCircle2 className="w-12 h-12 text-purple-500" />
            <p className="text-center text-gray-700 font-medium">Пароль изменён!</p>
            <p className="text-center text-sm text-gray-500">Перенаправляем на страницу входа…</p>
          </motion.div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="relative">
              <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                className="input-field pl-10"
                type="password"
                placeholder="Новый пароль (мин. 8 символов)"
                minLength={8}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoFocus
              />
            </div>
            <div className="relative">
              <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                className="input-field pl-10"
                type="password"
                placeholder="Повторите пароль"
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
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
                <>Сохранить пароль <ArrowRight className="w-4 h-4" /></>
              )}
            </motion.button>
          </form>
        )}

        <p className="text-center text-sm text-gray-500 mt-6">
          <Link to="/login" className="text-purple-600 font-semibold hover:text-purple-700">
            Вернуться ко входу
          </Link>
        </p>
      </motion.div>
    </div>
  );
}
