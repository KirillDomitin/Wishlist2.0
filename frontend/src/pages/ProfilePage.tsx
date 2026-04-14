import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { User, Lock, Save, Loader2, CheckCircle2 } from "lucide-react";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import { updateProfile, clearError } from "../store/authSlice";
import { Navbar } from "../components/Navbar";

export default function ProfilePage() {
  const dispatch = useAppDispatch();
  const { name: currentName, loading, error } = useAppSelector((s) => s.auth);

  const [name, setName] = useState(currentName ?? "");
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [localError, setLocalError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    setName(currentName ?? "");
    return () => { dispatch(clearError()); };
  }, [currentName]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);
    setSaved(false);

    if (newPassword && newPassword !== confirmPassword) {
      setLocalError("Новые пароли не совпадают");
      return;
    }

    const payload: { name?: string; current_password?: string; new_password?: string } = {};
    if (name.trim() && name.trim() !== currentName) payload.name = name.trim();
    if (newPassword) {
      payload.current_password = currentPassword;
      payload.new_password = newPassword;
    }

    if (!Object.keys(payload).length) return;

    const res = await dispatch(updateProfile(payload));
    if (res.meta.requestStatus === "fulfilled") {
      setSaved(true);
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      setTimeout(() => setSaved(false), 3000);
    }
  };

  const displayError = localError || error;

  return (
    <div className="page-bg min-h-screen">
      <Navbar />
      <div className="max-w-lg mx-auto px-4 py-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card rounded-3xl p-8"
        >
          <div className="flex items-center gap-3 mb-8">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center shadow-lg shadow-purple-200">
              <User className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold gradient-text">Профиль</h1>
              <p className="text-sm text-gray-500">Изменить имя или пароль</p>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Имя</label>
              <div className="relative">
                <User className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  className="input-field pl-10"
                  type="text"
                  placeholder="Ваше имя"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  minLength={1}
                  maxLength={100}
                />
              </div>
            </div>

            {/* Divider */}
            <div className="border-t border-purple-100 pt-4">
              <p className="text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
                <Lock className="w-4 h-4 text-purple-400" />
                Изменить пароль
                <span className="text-xs font-normal text-gray-400">(необязательно)</span>
              </p>
              <div className="space-y-3">
                <div className="relative">
                  <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    className="input-field pl-10"
                    type="password"
                    placeholder="Текущий пароль"
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                  />
                </div>
                <div className="relative">
                  <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    className="input-field pl-10"
                    type="password"
                    placeholder="Новый пароль (мин. 8 символов)"
                    minLength={8}
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                  />
                </div>
                <div className="relative">
                  <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    className="input-field pl-10"
                    type="password"
                    placeholder="Повторите новый пароль"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                  />
                </div>
              </div>
            </div>

            {displayError && (
              <motion.p
                initial={{ opacity: 0, y: -4 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-sm text-rose-500 text-center bg-rose-50 px-3 py-2 rounded-xl"
              >
                {displayError}
              </motion.p>
            )}

            {saved && (
              <motion.p
                initial={{ opacity: 0, y: -4 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-sm text-emerald-600 text-center bg-emerald-50 px-3 py-2 rounded-xl flex items-center justify-center gap-2"
              >
                <CheckCircle2 className="w-4 h-4" /> Сохранено!
              </motion.p>
            )}

            <motion.button
              type="submit"
              disabled={loading}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="btn-primary w-full justify-center py-3"
            >
              {loading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <><Save className="w-4 h-4" /> Сохранить</>
              )}
            </motion.button>
          </form>
        </motion.div>
      </div>
    </div>
  );
}
