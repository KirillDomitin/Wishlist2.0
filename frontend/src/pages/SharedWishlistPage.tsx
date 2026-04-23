import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { CalendarDays, Gift, Loader2, Link as LinkIcon } from "lucide-react";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import { fetchSharedWishlist, clearShared } from "../store/wishlistSlice";
import { createReservation } from "../store/reservationSlice";
import { Navbar } from "../components/Navbar";
import { WishlistItemCard } from "../components/WishlistItemCard";
import { ItemDetailModal } from "../components/ItemDetailModal";
import { Sparkles, useConfetti } from "../components/Sparkles";
import { useToast } from "../components/ui/Toaster";
import type { WishlistItem } from "../api/wishlists";

export default function SharedWishlistPage() {
  const { token } = useParams<{ token: string }>();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const { shared, loading } = useAppSelector((s) => s.wishlists);
  const isLoggedIn = !!useAppSelector((s) => s.auth.token);
  const { toast } = useToast();
  const fireConfetti = useConfetti();

  const [activeItem, setActiveItem] = useState<WishlistItem | null>(null);

  useEffect(() => {
    if (token) dispatch(fetchSharedWishlist(token));
    return () => { dispatch(clearShared()); };
  }, [token]);

  const handleReserve = async (itemId: string, quantity: number) => {
    if (!isLoggedIn) {
      navigate(`/register?redirect=/shared/${token}`);
      return;
    }
    const res = await dispatch(createReservation({ item_id: itemId, quantity }));
    if (res.meta.requestStatus === "fulfilled") {
      await fireConfetti();
      toast("Подарок забронирован! 🎉");
      if (token) dispatch(fetchSharedWishlist(token));
      setActiveItem(null);
    } else {
      const err = res.payload as string;
      toast(err || "Не удалось забронировать", "error");
    }
  };

  if (loading || !shared) {
    return (
      <div className="page-bg min-h-screen flex items-center justify-center relative">
        <Sparkles />
        {loading ? (
          <Loader2 className="w-10 h-10 animate-spin text-purple-400 z-10" />
        ) : (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-card rounded-3xl p-12 text-center z-10"
          >
            <Gift className="w-12 h-12 text-purple-400 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-gray-700">Список не найден</h2>
          </motion.div>
        )}
      </div>
    );
  }

  return (
    <div className="page-bg min-h-screen relative">
      <Sparkles />

      {/* Header */}
      {isLoggedIn ? (
        <Navbar />
      ) : (
        <motion.header
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="sticky top-0 z-30 glass-card border-b border-white/60 backdrop-blur-md"
        >
          <div className="max-w-2xl mx-auto px-4 h-16 flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center shadow-md">
              <Gift className="w-4 h-4 text-white" />
            </div>
            <span className="font-bold text-lg gradient-text">Wishlist</span>
          </div>
        </motion.header>
      )}

      <main className="max-w-2xl mx-auto px-4 py-8 relative z-10">
        {/* Wishlist header */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card rounded-2xl p-6 mb-6 text-center"
        >
          <motion.div
            animate={{ rotate: [0, -8, 8, -4, 4, 0] }}
            transition={{ duration: 1.5, delay: 0.4 }}
            className="w-14 h-14 rounded-2xl bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center mx-auto mb-4 shadow-lg shadow-purple-200"
          >
            <Gift className="w-7 h-7 text-white" />
          </motion.div>
          <h1 className="text-2xl font-bold text-gray-800">{shared.title}</h1>
          <p className="text-gray-500 mt-1 text-sm">
            {shared.items.length} {shared.items.length === 1 ? "желание" : shared.items.length < 5 ? "желания" : "желаний"} в списке
          </p>
          {shared.event_date && (() => {
            const today = new Date(); today.setHours(0, 0, 0, 0);
            const target = new Date(shared.event_date); target.setHours(0, 0, 0, 0);
            const diff = Math.round((target.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
            if (diff < 0) return null;
            const text = diff === 0 ? "сегодня!" : `через ${diff} ${diff === 1 ? "день" : diff < 5 ? "дня" : "дней"}`;
            return (
              <span className="inline-flex items-center gap-1.5 mt-2 text-xs font-medium text-teal-700 bg-teal-50 px-3 py-1 rounded-full">
                <CalendarDays className="w-3.5 h-3.5" />
                {text}
              </span>
            );
          })()}
        </motion.div>

        {/* Items */}
        {shared.items.length === 0 ? (
          <div className="glass-card rounded-2xl p-10 text-center text-gray-500">
            Список пока пуст
          </div>
        ) : (
          <div className="space-y-3">
            {[...shared.items].sort((a, b) => b.priority - a.priority).map((item, i) => (
              <WishlistItemCard
                key={item.id}
                item={item}
                isOwner={false}
                index={i}
                onOpen={setActiveItem}
              />
            ))}
          </div>
        )}

        <p className="text-center text-xs text-gray-400 mt-8 flex items-center justify-center gap-1">
          <LinkIcon className="w-3 h-3" />
          Powered by Wishlist
        </p>
      </main>

      <ItemDetailModal
        item={activeItem}
        onClose={() => setActiveItem(null)}
        onReserve={handleReserve}
        isLoggedIn={isLoggedIn}
      />
    </div>
  );
}
