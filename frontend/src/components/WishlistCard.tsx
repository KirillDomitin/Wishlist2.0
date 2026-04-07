import { motion } from "framer-motion";
import { Link, useNavigate } from "react-router-dom";
import { EyeOff, Gift, Share2, Trash2 } from "lucide-react";
import type { WishlistSummary } from "../api/wishlists";

interface Props {
  wishlist: WishlistSummary;
  onDelete: (id: string) => void;
  onShare: (token: string) => void;
  index: number;
}

export function WishlistCard({ wishlist, onDelete, onShare, index }: Props) {
  const navigate = useNavigate();
  const gradients = [
    "from-purple-400 to-pink-400",
    "from-rose-400 to-orange-400",
    "from-violet-400 to-indigo-400",
    "from-pink-400 to-rose-400",
    "from-amber-400 to-orange-400",
    "from-teal-400 to-cyan-400",
  ];
  const gradient = gradients[index % gradients.length];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.07 }}
      whileHover={{ y: -4, transition: { duration: 0.2 } }}
      onClick={() => navigate(`/wishlists/${wishlist.id}`)}
      className="glass-card rounded-2xl overflow-hidden group cursor-pointer"
    >
      {/* Color banner */}
      <div className={`h-2 bg-gradient-to-r ${gradient}`} />

      <div className="p-5">
        <div className="flex items-start justify-between gap-3 mb-3">
          <span className="font-semibold text-gray-800 group-hover:text-purple-700 transition-colors line-clamp-2 leading-snug">
            {wishlist.title}
          </span>
          <div className="flex gap-1 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              onClick={(e) => { e.stopPropagation(); onShare(wishlist.share_token); }}
              className="p-1.5 rounded-lg text-gray-400 hover:text-purple-600 hover:bg-purple-50 transition-colors"
              title="Скопировать ссылку"
            >
              <Share2 className="w-4 h-4" />
            </button>
            <button
              onClick={(e) => { e.stopPropagation(); onDelete(wishlist.id); }}
              className="p-1.5 rounded-lg text-gray-400 hover:text-rose-500 hover:bg-rose-50 transition-colors"
              title="Удалить"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        <div className="flex items-center gap-3 text-xs text-gray-500">
          <span className="flex items-center gap-1">
            <Gift className="w-3.5 h-3.5" />
            {wishlist.item_count} {wishlist.item_count === 1 ? "желание" : wishlist.item_count < 5 ? "желания" : "желаний"}
          </span>
          {wishlist.surprise_mode && (
            <span className="flex items-center gap-1 text-amber-600">
              <EyeOff className="w-3.5 h-3.5" />Сюрприз
            </span>
          )}
        </div>
      </div>
    </motion.div>
  );
}
