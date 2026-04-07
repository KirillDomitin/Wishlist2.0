import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Plus, Sparkles as SparklesIcon, Gift } from "lucide-react";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import {
  fetchMyWishlists,
  createWishlist,
  deleteWishlist,
} from "../store/wishlistSlice";
import { Navbar } from "../components/Navbar";
import { WishlistCard } from "../components/WishlistCard";
import { CreateWishlistModal } from "../components/CreateWishlistModal";
import { Sparkles } from "../components/Sparkles";
import { useToast } from "../components/ui/Toaster";

export default function DashboardPage() {
  const dispatch = useAppDispatch();
  const { list, loading } = useAppSelector((s) => s.wishlists);
  const [modalOpen, setModalOpen] = useState(false);
  const { toast } = useToast();

  useEffect(() => { dispatch(fetchMyWishlists()); }, []);

  const handleCreate = async (data: {
    title: string;
    surprise_mode: boolean;
  }) => {
    await dispatch(createWishlist(data));
    toast("Список создан! 🎉");
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Удалить список?")) return;
    await dispatch(deleteWishlist(id));
    toast("Список удалён", "error");
  };

  const handleShare = (token: string) => {
    const url = `${window.location.origin}/shared/${token}`;
    navigator.clipboard.writeText(url);
    toast("Ссылка скопирована! 🔗");
  };

  return (
    <div className="page-bg min-h-screen relative">
      <Sparkles />
      <Navbar />

      <main className="max-w-5xl mx-auto px-4 py-8 relative z-10">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -16 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between mb-8"
        >
          <div>
            <h1 className="text-3xl font-bold gradient-text">Мои списки</h1>
            <p className="text-gray-500 mt-1">
              {list.length === 0
                ? "Создайте первый список желаний"
                : `${list.length} ${list.length === 1 ? "список" : list.length < 5 ? "списка" : "списков"}`}
            </p>
          </div>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setModalOpen(true)}
            className="btn-primary"
          >
            <Plus className="w-4 h-4" />
            Новый список
          </motion.button>
        </motion.div>

        {/* Empty state */}
        {!loading && list.length === 0 && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-card rounded-3xl p-12 text-center"
          >
            <motion.div
              animate={{ y: [0, -12, 0] }}
              transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
              className="w-20 h-20 rounded-2xl bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center mx-auto mb-5 shadow-xl shadow-purple-200"
            >
              <Gift className="w-10 h-10 text-white" />
            </motion.div>
            <h2 className="text-xl font-bold text-gray-700 mb-2">Пока пусто</h2>
            <p className="text-gray-500 mb-6 max-w-xs mx-auto">
              Создайте список желаний и поделитесь им с близкими
            </p>
            <button onClick={() => setModalOpen(true)} className="btn-primary">
              <SparklesIcon className="w-4 h-4" />
              Создать первый список
            </button>
          </motion.div>
        )}

        {/* Loading skeleton */}
        {loading && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="glass-card rounded-2xl h-28 animate-pulse" />
            ))}
          </div>
        )}

        {/* Wishlists grid */}
        {!loading && list.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {list.map((w, i) => (
              <WishlistCard
                key={w.id}
                wishlist={w}
                index={i}
                onDelete={handleDelete}
                onShare={handleShare}
              />
            ))}
          </div>
        )}
      </main>

      <CreateWishlistModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onSubmit={handleCreate}
      />
    </div>
  );
}
