import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Bookmark, CheckCircle, XCircle, Loader2, ShoppingBag, RefreshCw } from "lucide-react";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import { fetchMyReservations, cancelReservation, createReservation } from "../store/reservationSlice";
import { Navbar } from "../components/Navbar";
import { Sparkles } from "../components/Sparkles";
import { ItemDetailModal } from "../components/ItemDetailModal";
import { useToast } from "../components/ui/Toaster";
import { useConfetti } from "../components/Sparkles";
import type { Reservation } from "../api/reservations";
import type { WishlistItem } from "../api/wishlists";

function reservationToItem(r: Reservation): WishlistItem | null {
  if (!r.item) return null;
  return {
    id: r.item_id,
    title: r.item.title,
    description: null,
    url: null,
    price: r.item.price,
    image_url: r.item.image_url,
    target_quantity: r.item.target_quantity,
    reserved_count: r.quantity,
    is_fully_reserved: false,
  };
}

export default function MyReservationsPage() {
  const dispatch = useAppDispatch();
  const { list, loading } = useAppSelector((s) => s.reservations);
  const { toast } = useToast();
  const fireConfetti = useConfetti();
  const [activeItem, setActiveItem] = useState<WishlistItem | null>(null);
  const [rebooking, setRebooking] = useState<string | null>(null);

  useEffect(() => { dispatch(fetchMyReservations()); }, []);

  const handleCancel = async (id: string) => {
    if (!confirm("Отменить бронирование?")) return;
    await dispatch(cancelReservation(id));
    toast("Бронирование отменено", "error");
  };

  const handleRebook = async (r: Reservation) => {
    setRebooking(r.id);
    const res = await dispatch(createReservation({ item_id: r.item_id, quantity: r.quantity }));
    setRebooking(null);
    if (res.meta.requestStatus === "fulfilled") {
      await fireConfetti();
      toast("Подарок снова забронирован! 🎉");
      dispatch(fetchMyReservations());
    } else {
      const err = res.payload as string;
      toast(err || "Не удалось забронировать", "error");
    }
  };

  const active = list.filter((r) => r.status === "active");
  const cancelled = list.filter((r) => r.status === "cancelled");

  return (
    <div className="page-bg min-h-screen relative">
      <Sparkles />
      <Navbar />

      <main className="max-w-2xl mx-auto px-4 py-8 relative z-10">
        <motion.div initial={{ opacity: 0, y: -12 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
          <h1 className="text-3xl font-bold gradient-text">Мои бронирования</h1>
          <p className="text-gray-500 mt-1">Подарки, которые вы забронировали</p>
        </motion.div>

        {loading && (
          <div className="flex justify-center py-16">
            <Loader2 className="w-8 h-8 animate-spin text-purple-400" />
          </div>
        )}

        {!loading && list.length === 0 && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-card rounded-3xl p-12 text-center"
          >
            <motion.div
              animate={{ y: [0, -10, 0] }}
              transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
              className="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center mx-auto mb-4 shadow-lg shadow-purple-200"
            >
              <Bookmark className="w-8 h-8 text-white" />
            </motion.div>
            <h2 className="text-xl font-bold text-gray-700 mb-2">Пока ничего</h2>
            <p className="text-gray-500 text-sm">
              Откройте чей-то список желаний и забронируйте подарок
            </p>
          </motion.div>
        )}

        {!loading && active.length > 0 && (
          <section className="mb-8">
            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
              Активные ({active.length})
            </h2>
            <div className="space-y-3">
              <AnimatePresence>
                {active.map((r, i) => (
                  <ReservationCard
                    key={r.id}
                    reservation={r}
                    index={i}
                    onOpen={() => { const item = reservationToItem(r); if (item) setActiveItem(item); }}
                    onCancel={() => handleCancel(r.id)}
                  />
                ))}
              </AnimatePresence>
            </div>
          </section>
        )}

        {!loading && cancelled.length > 0 && (
          <section>
            <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-3">
              Отменённые ({cancelled.length})
            </h2>
            <div className="space-y-2">
              {cancelled.map((r, i) => (
                <ReservationCard
                  key={r.id}
                  reservation={r}
                  index={i}
                  onOpen={() => { const item = reservationToItem(r); if (item) setActiveItem(item); }}
                  onRebook={r.item ? () => handleRebook(r) : undefined}
                  rebooking={rebooking === r.id}
                />
              ))}
            </div>
          </section>
        )}
      </main>

      <ItemDetailModal
        item={activeItem}
        onClose={() => setActiveItem(null)}
      />
    </div>
  );
}

interface CardProps {
  reservation: Reservation;
  index: number;
  onOpen: () => void;
  onCancel?: () => void;
  onRebook?: () => void;
  rebooking?: boolean;
}

function ReservationCard({ reservation: r, index: i, onOpen, onCancel, onRebook, rebooking }: CardProps) {
  const isCancelled = r.status === "cancelled";
  const hasItem = !!r.item;

  return (
    <motion.div
      key={r.id}
      initial={{ opacity: 0, x: -16 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 16 }}
      transition={{ delay: i * 0.05 }}
      onClick={hasItem ? onOpen : undefined}
      className={`glass-card rounded-2xl p-4 flex items-center gap-4 ${
        isCancelled ? "opacity-60" : ""
      } ${hasItem ? "cursor-pointer hover:shadow-xl hover:shadow-purple-100/50 transition-shadow" : ""}`}
    >
      {/* Thumbnail */}
      <div className={`w-14 h-14 rounded-xl overflow-hidden shrink-0 flex items-center justify-center ${
        isCancelled ? "bg-gray-100" : "bg-gradient-to-br from-purple-100 to-pink-100"
      }`}>
        {r.item?.image_url ? (
          <img src={r.item.image_url} alt={r.item.title} className="w-full h-full object-cover" />
        ) : (
          <ShoppingBag className={`w-6 h-6 ${isCancelled ? "text-gray-300" : "text-purple-300"}`} />
        )}
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold text-gray-800 truncate">
          {r.item?.title || "Подарок"}
        </p>
        <div className="flex items-center gap-2 mt-0.5 flex-wrap">
          {r.item?.price != null && (
            <span className="text-xs font-medium text-purple-600">
              {Number(r.item.price).toLocaleString("ru-RU")} ₽
            </span>
          )}
          <span className="text-xs text-gray-400">
            Кол-во: <span className="font-medium text-gray-600">{r.quantity}</span>
          </span>
        </div>
      </div>

      {/* Status + action */}
      <div className="flex items-center gap-2 shrink-0">
        {isCancelled ? (
          <div className="flex items-center gap-2">
            <span className="flex items-center gap-1 text-xs font-medium text-gray-400 bg-gray-50 px-2 py-1 rounded-full">
              <XCircle className="w-3.5 h-3.5" />
              Отменено
            </span>
            {onRebook && (
              <button
                onClick={(e) => { e.stopPropagation(); onRebook(); }}
                disabled={rebooking}
                className="flex items-center gap-1 text-xs font-medium text-purple-600 hover:text-purple-700 hover:bg-purple-50 px-2 py-1 rounded-lg transition-colors disabled:opacity-50"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${rebooking ? "animate-spin" : ""}`} />
                {rebooking ? "..." : "Снова"}
              </button>
            )}
          </div>
        ) : (
          <>
            <span className="flex items-center gap-1 text-xs font-medium text-green-600 bg-green-50 px-2 py-1 rounded-full">
              <CheckCircle className="w-3.5 h-3.5" />
              Активно
            </span>
            {onCancel && (
              <button
                onClick={(e) => { e.stopPropagation(); onCancel(); }}
                className="text-xs text-rose-500 hover:text-rose-600 hover:bg-rose-50 px-2 py-1 rounded-lg transition-colors"
              >
                Отменить
              </button>
            )}
          </>
        )}
      </div>
    </motion.div>
  );
}
