import { useEffect, useState, useCallback, useRef } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  Plus,
  Share2,
  EyeOff,
  Loader2,
} from "lucide-react";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import {
  fetchWishlistDetail,
  addItem,
  updateItem,
  deleteItem,
  clearCurrent,
} from "../store/wishlistSlice";
import { Navbar } from "../components/Navbar";
import { WishlistItemCard } from "../components/WishlistItemCard";
import { AddItemModal } from "../components/AddItemModal";
import { Sparkles } from "../components/Sparkles";
import { useToast } from "../components/ui/Toaster";
import type { WishlistItem, WishlistItemCreate } from "../api/wishlists";
import { reservationApi } from "../api/reservations";
import { usersApi } from "../api/users";

export interface ReserverInfo {
  name: string;
  quantity: number;
}

export default function WishlistDetailPage() {
  const { id } = useParams<{ id: string }>();
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const { current } = useAppSelector((s) => s.wishlists);
  const { toast } = useToast();

  const [addOpen, setAddOpen] = useState(false);
  const [editItem, setEditItem] = useState<WishlistItem | null>(null);
  const [reserversByItem, setReserversByItem] = useState<Record<string, ReserverInfo[]>>({});
  const surpriseModeRef = useRef(false);

  const loadReservers = useCallback(async (wishlistId: string) => {
    if (surpriseModeRef.current) return;
    try {
      const reservations = await reservationApi.listForWishlist(wishlistId);
      const uniqueReserverIds = [...new Set(reservations.map((r) => r.reserver_id))];
      const userMap: Record<string, string> = {};
      await Promise.all(
        uniqueReserverIds.map(async (userId) => {
          try {
            const user = await usersApi.getById(userId);
            userMap[userId] = user.name;
          } catch {
            userMap[userId] = "Аноним";
          }
        })
      );
      const grouped: Record<string, ReserverInfo[]> = {};
      for (const r of reservations) {
        if (!grouped[r.item_id]) grouped[r.item_id] = [];
        grouped[r.item_id].push({ name: userMap[r.reserver_id] ?? "Аноним", quantity: r.quantity });
      }
      setReserversByItem(grouped);
    } catch {
      // silently ignore
    }
  }, []);

  useEffect(() => {
    if (!id) return;
    dispatch(fetchWishlistDetail(id));
    const interval = setInterval(() => {
      dispatch(fetchWishlistDetail(id));
      loadReservers(id);
    }, 5000);
    return () => {
      clearInterval(interval);
      dispatch(clearCurrent());
    };
  }, [id]);

  useEffect(() => {
    if (!current || !id) return;
    surpriseModeRef.current = current.surprise_mode;
    loadReservers(id);
  }, [current?.surprise_mode, id]);

  const handleAddItem = async (data: WishlistItemCreate) => {
    if (!id) return;
    await dispatch(addItem({ wishlistId: id, data }));
    toast("Желание добавлено! ✨");
  };

  const handleUpdateItem = async (data: WishlistItemCreate) => {
    if (!id || !editItem) return;
    await dispatch(updateItem({ wishlistId: id, itemId: editItem.id, data }));
    setEditItem(null);
    toast("Желание обновлено");
  };

  const handleDeleteItem = async (itemId: string) => {
    if (!id || !confirm("Удалить желание?")) return;
    await dispatch(deleteItem({ wishlistId: id, itemId }));
    toast("Удалено", "error");
  };

  const handleShare = () => {
    if (!current) return;
    const url = `${window.location.origin}/shared/${current.share_token}`;
    navigator.clipboard.writeText(url);
    toast("Ссылка скопирована! 🔗");
  };

  if (!current) {
    return (
      <div className="page-bg min-h-screen">
        <Navbar />
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-purple-400" />
        </div>
      </div>
    );
  }

  return (
    <div className="page-bg min-h-screen relative">
      <Sparkles />
      <Navbar />

      <main className="max-w-2xl mx-auto px-4 py-8 relative z-10">
        {/* Back + header */}
        <motion.div initial={{ opacity: 0, y: -12 }} animate={{ opacity: 1, y: 0 }}>
          <button
            onClick={() => navigate("/")}
            className="btn-ghost mb-4 -ml-2 text-gray-500"
          >
            <ArrowLeft className="w-4 h-4" /> Назад
          </button>

          <div className="glass-card rounded-2xl p-5 mb-6">
            <div className="flex items-start justify-between gap-3">
              <div>
                <h1 className="text-2xl font-bold text-gray-800">{current.title}</h1>
                {current.surprise_mode && (
                  <div className="flex items-center gap-3 mt-2">
                    <span className="flex items-center gap-1 text-xs text-amber-600">
                      <EyeOff className="w-3.5 h-3.5" />Режим сюрприза
                    </span>
                  </div>
                )}
              </div>

              <div className="flex gap-2">
                <button onClick={handleShare} className="btn-secondary text-xs px-3 py-2">
                  <Share2 className="w-3.5 h-3.5" /> Поделиться
                </button>
                <button
                  onClick={() => setAddOpen(true)}
                  className="btn-primary text-xs px-3 py-2"
                >
                  <Plus className="w-3.5 h-3.5" /> Добавить
                </button>
              </div>
            </div>

            {current.surprise_mode && (
              <p className="mt-3 text-xs text-amber-700 bg-amber-50 px-3 py-2 rounded-xl">
                🎁 Режим сюрприза включён — вы не видите, кто и что забронировал
              </p>
            )}
          </div>
        </motion.div>

        {/* Items */}
        {current.items.length === 0 ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="glass-card rounded-2xl p-10 text-center"
          >
            <p className="text-gray-500 mb-4">Список пуст. Добавьте первое желание!</p>
            <button onClick={() => setAddOpen(true)} className="btn-primary">
              <Plus className="w-4 h-4" /> Добавить желание
            </button>
          </motion.div>
        ) : (
          <div className="space-y-3">
            {current.items.map((item, i) => (
              <WishlistItemCard
                key={item.id}
                item={item}
                isOwner={true}
                index={i}
                onEdit={(item) => setEditItem(item)}
                onDelete={handleDeleteItem}
                reservers={!current.surprise_mode ? (reserversByItem[item.id] ?? []) : undefined}
              />
            ))}
          </div>
        )}
      </main>

      <AddItemModal
        open={addOpen}
        onClose={() => setAddOpen(false)}
        onSubmit={handleAddItem}
      />
      <AddItemModal
        open={!!editItem}
        onClose={() => setEditItem(null)}
        editItem={editItem}
        onSubmit={handleUpdateItem}
      />
    </div>
  );
}
