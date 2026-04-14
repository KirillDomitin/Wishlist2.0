import { useState, useEffect, useRef } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Gift, Mail, Lock, User, ArrowRight, Loader2, ShieldCheck } from "lucide-react";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import { register, verifyEmail, clearError } from "../store/authSlice";
import { Sparkles } from "../components/Sparkles";

export default function RegisterPage() {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { loading, error, token } = useAppSelector((s) => s.auth);

  const redirectRef = useRef(searchParams.get("redirect") || "/");

  // Step 1 fields
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [passwordError, setPasswordError] = useState("");

  // Step 2
  const [step, setStep] = useState<1 | 2>(1);
  const [code, setCode] = useState("");

  useEffect(() => {
    if (token) navigate(redirectRef.current, { replace: true });
    return () => { dispatch(clearError()); };
  }, []);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      setPasswordError("Пароли не совпадают");
      return;
    }
    setPasswordError("");
    const res = await dispatch(register({ name, email, password }));
    if (res.meta.requestStatus === "fulfilled") setStep(2);
  };

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await dispatch(verifyEmail({ email, code }));
    if (res.meta.requestStatus === "fulfilled") navigate(redirectRef.current, { replace: true });
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
            {step === 1 ? (
              <Gift className="w-8 h-8 text-white" />
            ) : (
              <ShieldCheck className="w-8 h-8 text-white" />
            )}
          </motion.div>
          <h1 className="text-2xl font-bold gradient-text">
            {step === 1 ? "Создать аккаунт" : "Подтверждение"}
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            {step === 1 ? "Начните делиться желаниями" : `Код отправлен на ${email}`}
          </p>
        </div>

        <AnimatePresence mode="wait">
          {step === 1 ? (
            <motion.form
              key="step1"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              onSubmit={handleRegister}
              className="space-y-4"
            >
              <div className="relative">
                <User className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  className="input-field pl-10"
                  placeholder="Ваше имя"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  autoFocus
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
              <div className="relative">
                <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  className="input-field pl-10"
                  type="password"
                  placeholder="Повторите пароль"
                  value={confirmPassword}
                  onChange={(e) => { setConfirmPassword(e.target.value); setPasswordError(""); }}
                  required
                />
              </div>

              {(passwordError || error) && (
                <motion.p
                  initial={{ opacity: 0, y: -4 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-sm text-rose-500 text-center bg-rose-50 px-3 py-2 rounded-xl"
                >
                  {passwordError || error}
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
                  <>Далее <ArrowRight className="w-4 h-4" /></>
                )}
              </motion.button>
            </motion.form>
          ) : (
            <motion.form
              key="step2"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              onSubmit={handleVerify}
              className="space-y-4"
            >
              <p className="text-xs text-gray-500 text-center">
                Введите 6-значный код из письма. Код действителен 15 минут.
              </p>
              <input
                className="input-field text-center text-2xl tracking-[0.5em] font-mono"
                placeholder="000000"
                value={code}
                onChange={(e) => setCode(e.target.value.replace(/\D/g, "").slice(0, 6))}
                maxLength={6}
                inputMode="numeric"
                autoFocus
                required
              />

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
                disabled={loading || code.length !== 6}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="btn-primary w-full justify-center py-3"
              >
                {loading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <>Подтвердить <ArrowRight className="w-4 h-4" /></>
                )}
              </motion.button>

              <button
                type="button"
                onClick={() => { setStep(1); setCode(""); dispatch(clearError()); }}
                className="w-full text-sm text-gray-400 hover:text-gray-600 transition-colors"
              >
                ← Изменить данные
              </button>
            </motion.form>
          )}
        </AnimatePresence>

        <p className="text-center text-sm text-gray-500 mt-6">
          Уже есть аккаунт?{" "}
          <Link
            to={redirectRef.current !== "/" ? `/login?redirect=${encodeURIComponent(redirectRef.current)}` : "/login"}
            className="text-purple-600 font-semibold hover:text-purple-700"
          >
            Войти
          </Link>
        </p>
      </motion.div>
    </div>
  );
}
