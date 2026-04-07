import { motion } from "framer-motion";
import {
  ExternalLink,
  Pencil,
  Trash2,
  Users,
  CheckCircle,
  ShoppingBag,
  User,
} from "lucide-react";
import type { WishlistItem } from "../api/wishlists";
import type { ReserverInfo } from "../pages/WishlistDetailPage";

interface Props {
  item: WishlistItem;
  isOwner: boolean;
  onReserve?: (item: WishlistItem) => void;
  onEdit?: (item: WishlistItem) => void;
  onDelete?: (id: string) => void;
  onOpen?: (item: WishlistItem) => void;
  index: number;
  reservers?: ReserverInfo[];
}

export function WishlistItemCard({
  item,
  isOwner,
  onReserve,
  onEdit,
  onDelete,
  onOpen,
  index,
  reservers,
}: Props) {
  const progressPct =
    item.target_quantity > 0
      ? Math.min((item.reserved_count / item.target_quantity) * 100, 100)
      : 0;

  return (
    <motion.div
      initial={{ opacity: 0, x: -16 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.06 }}
      onClick={onOpen ? () => onOpen(item) : undefined}
      className={`glass-card rounded-2xl p-4 flex gap-4 group ${
        item.is_fully_reserved ? "opacity-75" : ""
      } ${onOpen ? "cursor-pointer hover:shadow-2xl hover:shadow-purple-100/60 transition-shadow" : ""}`}
    >
      {/* Image or placeholder */}
      <div className="shrink-0 w-16 h-16 rounded-xl overflow-hidden bg-gradient-to-br from-purple-100 to-pink-100 flex items-center justify-center">
        {item.image_url ? (
          <img
            src={item.image_url}
            alt={item.title}
            className="w-full h-full object-cover"
          />
        ) : (
          <ShoppingBag className="w-7 h-7 text-purple-300" />
        )}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0">
            <h3 className="font-semibold text-gray-800 truncate">{item.title}</h3>
            {item.description && (
              <p className="text-xs text-gray-500 mt-0.5 line-clamp-1">{item.description}</p>
            )}
          </div>

          <div className="flex gap-1 shrink-0">
            {item.url && (
              <a
                href={item.url}
                target="_blank"
                rel="noopener noreferrer"
                className="p-1.5 rounded-lg text-gray-400 hover:text-purple-600 hover:bg-purple-50 transition-colors"
              >
                <ExternalLink className="w-4 h-4" />
              </a>
            )}
            {isOwner && onEdit && (
              <button
                onClick={() => onEdit(item)}
                className="p-1.5 rounded-lg text-gray-400 hover:text-purple-600 hover:bg-purple-50 transition-colors opacity-0 group-hover:opacity-100"
              >
                <Pencil className="w-4 h-4" />
              </button>
            )}
            {isOwner && onDelete && (
              <button
                onClick={() => onDelete(item.id)}
                className="p-1.5 rounded-lg text-gray-400 hover:text-rose-500 hover:bg-rose-50 transition-colors opacity-0 group-hover:opacity-100"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        <div className="flex items-center gap-3 mt-2 flex-wrap">
          {item.price != null && (
            <span className="text-sm font-bold text-purple-700">
              {Number(item.price).toLocaleString("ru-RU")} ₽
            </span>
          )}

          {item.target_quantity > 1 && (
            <span className="flex items-center gap-1 text-xs text-gray-500">
              <Users className="w-3.5 h-3.5" />
              {item.reserved_count}/{item.target_quantity}
            </span>
          )}

          {item.is_fully_reserved ? (
            <span className="flex items-center gap-1 text-xs font-medium text-green-600 bg-green-50 px-2 py-0.5 rounded-full">
              <CheckCircle className="w-3.5 h-3.5" />
              Забронировано
            </span>
          ) : (
            !isOwner && onReserve && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => onReserve(item)}
                className="text-xs font-semibold px-3 py-1 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-sm shadow-purple-200 hover:shadow-purple-300 transition-shadow"
              >
                Забронировать
              </motion.button>
            )
          )}
        </div>

        {/* Progress bar for collective gifts */}
        {item.target_quantity > 1 && (
          <div className="mt-2 h-1.5 bg-purple-100 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${progressPct}%` }}
              transition={{ duration: 0.6, ease: "easeOut" }}
              className="h-full bg-gradient-to-r from-purple-400 to-pink-400 rounded-full"
            />
          </div>
        )}

        {/* Reserver names (owner view only) */}
        {isOwner && reservers && reservers.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1.5">
            {reservers.map((r, idx) => (
              <span
                key={idx}
                className="flex items-center gap-1 text-xs bg-purple-50 text-purple-700 px-2 py-0.5 rounded-full border border-purple-100"
              >
                <User className="w-3 h-3" />
                {r.name}{r.quantity > 1 ? ` ×${r.quantity}` : ""}
              </span>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
}
