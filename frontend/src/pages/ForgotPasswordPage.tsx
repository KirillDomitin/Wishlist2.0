import { useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Gift, Mail, ArrowRight, Loader2, CheckCircle2 } from "lucide-react";
import { authApi } from "../api/auth";
import { Sparkles } from "../components/Sparkles";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await authApi.forgotPassword(email);
      setSent(true);
    } catch {
      setError("Произошла ошибка. Попробуйте позже.");
    } finally {
      setLoading(false);
    }
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
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center shadow-xl shadow-purple-200 mb-4">
            <Gift className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold gradient-text">Сброс пароля</h1>
          <p className="text-sm text-gray-500 mt-1 text-center">
            Введите email — пришлём ссылку для сброса
          </p>
        </div>

        {sent ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex flex-col items-center gap-3 py-4"
          >
            <CheckCircle2 className="w-12 h-12 text-purple-500" />
            <p className="text-center text-gray-700 font-medium">Письмо отправлено!</p>
            <p className="text-center text-sm text-gray-500">
              Проверьте почту <span className="font-semibold text-purple-600">{email}</span> и
              перейдите по ссылке из письма.
            </p>
          </motion.div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="relative">
              <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                className="input-field pl-10"
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoFocus
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
                <>Отправить ссылку <ArrowRight className="w-4 h-4" /></>
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
