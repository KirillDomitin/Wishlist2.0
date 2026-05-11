import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { ShieldCheck, Users, List, ScrollText, Pencil, Trash2, RefreshCw } from "lucide-react";
import { Navbar } from "../components/Navbar";
import { Sparkles } from "../components/Sparkles";
import { Modal } from "../components/ui/Modal";
import { adminApi, type AdminUser, type AdminWishlist, type LogEntry, type AdminWishlistUpdateRequest } from "../api/admin";

type Tab = "users" | "wishlists" | "logs";

const LEVEL_COLORS: Record<string, string> = {
  DEBUG: "text-gray-400",
  INFO: "text-blue-500",
  WARNING: "text-yellow-500",
  ERROR: "text-red-500",
  CRITICAL: "text-red-700 font-bold",
};

// ── Users tab ─────────────────────────────────────────────────────────────────

function UsersTab() {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [editUser, setEditUser] = useState<AdminUser | null>(null);
  const [form, setForm] = useState({ name: "", email: "", is_admin: false });
  const [saving, setSaving] = useState(false);

  const load = () => adminApi.getUsers().then(setUsers);
  useEffect(() => { load(); }, []);

  const openEdit = (u: AdminUser) => {
    setEditUser(u);
    setForm({ name: u.name, email: u.email, is_admin: u.is_admin });
  };

  const handleSave = async () => {
    if (!editUser) return;
    setSaving(true);
    try {
      await adminApi.updateUser(editUser.id, form);
      await load();
      setEditUser(null);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (u: AdminUser) => {
    if (!confirm(`Удалить пользователя ${u.email}?`)) return;
    await adminApi.deleteUser(u.id);
    await load();
  };

  return (
    <>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-500 border-b border-white/40">
              <th className="py-2 pr-4 font-medium">Имя</th>
              <th className="py-2 pr-4 font-medium">Email</th>
              <th className="py-2 pr-4 font-medium">Роль</th>
              <th className="py-2 pr-4 font-medium">Дата</th>
              <th className="py-2 font-medium" />
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id} className="border-b border-white/20 hover:bg-white/20 transition-colors">
                <td className="py-2 pr-4 font-medium text-gray-800">{u.name}</td>
                <td className="py-2 pr-4 text-gray-600">{u.email}</td>
                <td className="py-2 pr-4">
                  {u.is_admin
                    ? <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full font-semibold">Admin</span>
                    : <span className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full">User</span>}
                </td>
                <td className="py-2 pr-4 text-gray-400 text-xs">{new Date(u.created_at).toLocaleDateString("ru")}</td>
                <td className="py-2 flex gap-1 justify-end">
                  <button onClick={() => openEdit(u)} className="p-1.5 rounded-lg text-gray-400 hover:text-purple-600 hover:bg-purple-50 transition-colors">
                    <Pencil className="w-4 h-4" />
                  </button>
                  <button onClick={() => handleDelete(u)} className="p-1.5 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 transition-colors">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <Modal open={!!editUser} onClose={() => setEditUser(null)} title="Редактировать пользователя">
        <div className="space-y-3">
          <div>
            <label className="text-sm text-gray-600 mb-1 block">Имя</label>
            <input
              className="input-field w-full"
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
            />
          </div>
          <div>
            <label className="text-sm text-gray-600 mb-1 block">Email</label>
            <input
              className="input-field w-full"
              value={form.email}
              onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
            />
          </div>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={form.is_admin}
              onChange={(e) => setForm((f) => ({ ...f, is_admin: e.target.checked }))}
              className="w-4 h-4 accent-purple-500"
            />
            <span className="text-sm text-gray-700">Администратор</span>
          </label>
          <button onClick={handleSave} disabled={saving} className="btn-primary w-full mt-2">
            {saving ? "Сохранение..." : "Сохранить"}
          </button>
        </div>
      </Modal>
    </>
  );
}

// ── Wishlists tab ─────────────────────────────────────────────────────────────

function WishlistsTab() {
  const [wishlists, setWishlists] = useState<AdminWishlist[]>([]);
  const [userMap, setUserMap] = useState<Record<string, AdminUser>>({});
  const [editWishlist, setEditWishlist] = useState<AdminWishlist | null>(null);
  const [form, setForm] = useState<AdminWishlistUpdateRequest>({});
  const [saving, setSaving] = useState(false);

  const load = () =>
    Promise.all([adminApi.getWishlists(), adminApi.getUsers()]).then(([wl, users]) => {
      setWishlists(wl);
      setUserMap(Object.fromEntries(users.map((u) => [u.id, u])));
    });

  useEffect(() => { load(); }, []);

  const openEdit = (w: AdminWishlist) => {
    setEditWishlist(w);
    setForm({
      title: w.title,
      is_public: w.is_public,
      surprise_mode: w.surprise_mode,
      event_date: w.event_date,
    });
  };

  const handleSave = async () => {
    if (!editWishlist) return;
    setSaving(true);
    try {
      await adminApi.updateWishlist(editWishlist.id, form);
      await load();
      setEditWishlist(null);
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-500 border-b border-white/40">
              <th className="py-2 pr-4 font-medium">Название</th>
              <th className="py-2 pr-4 font-medium">Владелец</th>
              <th className="py-2 pr-4 font-medium">Предметов</th>
              <th className="py-2 pr-4 font-medium">Статус</th>
              <th className="py-2 pr-4 font-medium">Дата события</th>
              <th className="py-2 pr-4 font-medium">Создан</th>
              <th className="py-2 font-medium" />
            </tr>
          </thead>
          <tbody>
            {wishlists.map((w) => {
              const owner = userMap[w.owner_id];
              return (
                <tr key={w.id} className="border-b border-white/20 hover:bg-white/20 transition-colors">
                  <td className="py-2 pr-4 font-medium text-gray-800">{w.title}</td>
                  <td className="py-2 pr-4">
                    {owner ? (
                      <div>
                        <div className="text-gray-800 font-medium">{owner.name}</div>
                        <div className="text-gray-400 text-xs">{owner.email}</div>
                      </div>
                    ) : (
                      <span className="text-gray-400 text-xs font-mono">{w.owner_id.slice(0, 8)}…</span>
                    )}
                  </td>
                  <td className="py-2 pr-4 text-center">
                    <span className="bg-purple-100 text-purple-700 text-xs px-2 py-0.5 rounded-full">{w.item_count}</span>
                  </td>
                  <td className="py-2 pr-4">
                    {w.is_public
                      ? <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">Публичный</span>
                      : <span className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full">Приватный</span>}
                    {w.surprise_mode && <span className="ml-1 text-xs bg-pink-100 text-pink-600 px-2 py-0.5 rounded-full">Сюрприз</span>}
                  </td>
                  <td className="py-2 pr-4 text-gray-400 text-xs">
                    {w.event_date ? new Date(w.event_date).toLocaleDateString("ru") : "—"}
                  </td>
                  <td className="py-2 pr-4 text-gray-400 text-xs">{new Date(w.created_at).toLocaleDateString("ru")}</td>
                  <td className="py-2">
                    <button onClick={() => openEdit(w)} className="p-1.5 rounded-lg text-gray-400 hover:text-purple-600 hover:bg-purple-50 transition-colors">
                      <Pencil className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <Modal open={!!editWishlist} onClose={() => setEditWishlist(null)} title="Редактировать вишлист">
        <div className="space-y-3">
          <div>
            <label className="text-sm text-gray-600 mb-1 block">Название</label>
            <input
              className="input-field w-full"
              value={form.title ?? ""}
              onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
            />
          </div>
          <div>
            <label className="text-sm text-gray-600 mb-1 block">Дата события</label>
            <input
              type="date"
              className="input-field w-full"
              value={form.event_date ?? ""}
              onChange={(e) => setForm((f) => ({ ...f, event_date: e.target.value || null }))}
            />
          </div>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={form.is_public ?? true}
              onChange={(e) => setForm((f) => ({ ...f, is_public: e.target.checked }))}
              className="w-4 h-4 accent-purple-500"
            />
            <span className="text-sm text-gray-700">Публичный</span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={form.surprise_mode ?? false}
              onChange={(e) => setForm((f) => ({ ...f, surprise_mode: e.target.checked }))}
              className="w-4 h-4 accent-pink-500"
            />
            <span className="text-sm text-gray-700">Режим сюрприза</span>
          </label>
          <button onClick={handleSave} disabled={saving} className="btn-primary w-full mt-2">
            {saving ? "Сохранение..." : "Сохранить"}
          </button>
        </div>
      </Modal>
    </>
  );
}

// ── Logs tab ──────────────────────────────────────────────────────────────────

const SERVICES = ["all", "user-service", "wishlist-service", "reservation-service"];
const LEVELS = ["all", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"];

function LogsTab() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [service, setService] = useState("all");
  const [level, setLevel] = useState("all");
  const [limit, setLimit] = useState(200);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const data = await adminApi.getLogs({ service, level, limit });
      setLogs(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-2 items-center">
        <select value={service} onChange={(e) => setService(e.target.value)} className="input-field text-sm py-1.5">
          {SERVICES.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
        <select value={level} onChange={(e) => setLevel(e.target.value)} className="input-field text-sm py-1.5">
          {LEVELS.map((l) => <option key={l} value={l}>{l}</option>)}
        </select>
        <input
          type="number"
          value={limit}
          onChange={(e) => setLimit(Number(e.target.value))}
          min={1} max={2000}
          className="input-field text-sm py-1.5 w-24"
          placeholder="Лимит"
        />
        <button onClick={load} disabled={loading} className="btn-ghost text-sm gap-1.5">
          <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          Обновить
        </button>
        <span className="text-xs text-gray-400 ml-auto">{logs.length} записей</span>
      </div>

      <div className="overflow-x-auto max-h-[480px] overflow-y-auto rounded-xl border border-white/40">
        <table className="w-full text-xs font-mono">
          <thead className="sticky top-0 bg-white/80 backdrop-blur-sm">
            <tr className="text-left text-gray-500 border-b border-white/40">
              <th className="py-2 px-3 font-medium">Время</th>
              <th className="py-2 px-3 font-medium">Уровень</th>
              <th className="py-2 px-3 font-medium">Сервис</th>
              <th className="py-2 px-3 font-medium">Сообщение</th>
            </tr>
          </thead>
          <tbody>
            {logs.length === 0 && (
              <tr><td colSpan={4} className="py-8 text-center text-gray-400 text-sm">Нет записей</td></tr>
            )}
            {logs.map((l, i) => (
              <tr key={i} className="border-b border-white/10 hover:bg-white/20">
                <td className="py-1.5 px-3 text-gray-400 whitespace-nowrap">{l.timestamp}</td>
                <td className={`py-1.5 px-3 whitespace-nowrap ${LEVEL_COLORS[l.level] ?? "text-gray-500"}`}>{l.level}</td>
                <td className="py-1.5 px-3 text-purple-600 whitespace-nowrap">{l.service}</td>
                <td className="py-1.5 px-3 text-gray-700 break-all">{l.message}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ── AdminPage ─────────────────────────────────────────────────────────────────

const TABS: { id: Tab; label: string; icon: React.ReactNode }[] = [
  { id: "users", label: "Пользователи", icon: <Users className="w-4 h-4" /> },
  { id: "wishlists", label: "Вишлисты", icon: <List className="w-4 h-4" /> },
  { id: "logs", label: "Логи", icon: <ScrollText className="w-4 h-4" /> },
];

export default function AdminPage() {
  const [tab, setTab] = useState<Tab>("users");

  return (
    <div className="page-bg min-h-screen relative">
      <Sparkles />
      <Navbar />
      <main className="max-w-6xl mx-auto px-4 py-8 relative z-10">
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-2 mb-6">
            <ShieldCheck className="w-6 h-6 text-purple-500" />
            <h1 className="text-2xl font-bold gradient-text">Панель администратора</h1>
          </div>

          <div className="glass-card rounded-2xl p-6">
            <div className="flex gap-1 mb-6 border-b border-white/40 pb-4">
              {TABS.map((t) => (
                <button
                  key={t.id}
                  onClick={() => setTab(t.id)}
                  className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
                    tab === t.id
                      ? "bg-purple-100 text-purple-700"
                      : "text-gray-500 hover:text-gray-700 hover:bg-white/60"
                  }`}
                >
                  {t.icon}
                  {t.label}
                </button>
              ))}
            </div>

            {tab === "users" && <UsersTab />}
            {tab === "wishlists" && <WishlistsTab />}
            {tab === "logs" && <LogsTab />}
          </div>
        </motion.div>
      </main>
    </div>
  );
}
