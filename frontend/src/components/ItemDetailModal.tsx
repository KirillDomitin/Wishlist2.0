import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronLeft, ChevronRight } from "lucide-react";
import {
  X,
  ExternalLink,
  ShoppingBag,
  Users,
  CheckCircle,
  Gift,
  LogIn,
} from "lucide-react";
import type { WishlistItem } from "../api/wishlists";

interface Props {
  item: WishlistItem | null;
  onClose: () => void;
  onReserve?: (itemId: string, quantity: number) => Promise<void>;
  isLoggedIn?: boolean;
}

export function ItemDetailModal({ item, onClose, onReserve, isLoggedIn = true }: Props) {
  const [quantity, setQuantity] = useState(1);
  const [loading, setLoading] = useState(false);
  const [imgIndex, setImgIndex] = useState(0);

  if (!item) return null;

  const images = item.image_urls ?? [];
  const available = item.target_quantity - item.reserved_count;
  const progressPct = item.target_quantity > 0
    ? Math.min((item.reserved_count / item.target_quantity) * 100, 100)
    : 0;

  const handleReserve = async () => {
    if (!onReserve) return;
    setLoading(true);
    await onReserve(item.id, quantity);
    setLoading(false);
    setQuantity(1);
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
        className="fixed inset-0 bg-black/30 backdrop-blur-sm z-40"
      />
      <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4">
        <motion.div
          initial={{ opacity: 0, y: 60 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 60 }}
          transition={{ type: "spring", stiffness: 380, damping: 32 }}
          onClick={(e) => e.stopPropagation()}
          className="glass-card w-full sm:max-w-md rounded-t-3xl sm:rounded-3xl overflow-hidden"
        >
          {/* Image area */}
          <div className="relative h-52 bg-gradient-to-br from-purple-100 via-pink-50 to-amber-50 flex items-center justify-center overflow-hidden">
            {images.length > 0 ? (
              <img
                src={images[imgIndex]}
                alt={item.title}
                className="w-full h-full object-cover"
              />
            ) : (
              <motion.div
                animate={{ y: [0, -8, 0] }}
                transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
              >
                <ShoppingBag className="w-20 h-20 text-purple-200" />
              </motion.div>
            )}

            {/* Carousel controls */}
            {images.length > 1 && (
              <>
                <button
                  onClick={(e) => { e.stopPropagation(); setImgIndex((i) => (i - 1 + images.length) % images.length); }}
                  className="absolute left-2 top-1/2 -translate-y-1/2 w-7 h-7 rounded-full bg-white/80 flex items-center justify-center text-gray-600 hover:bg-white shadow-sm"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <button
                  onClick={(e) => { e.stopPropagation(); setImgIndex((i) => (i + 1) % images.length); }}
                  className="absolute right-10 top-1/2 -translate-y-1/2 w-7 h-7 rounded-full bg-white/80 flex items-center justify-center text-gray-600 hover:bg-white shadow-sm"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
                <div className="absolute bottom-2 left-1/2 -translate-x-1/2 flex gap-1">
                  {images.map((_, i) => (
                    <button
                      key={i}
                      onClick={(e) => { e.stopPropagation(); setImgIndex(i); }}
                      className={`w-1.5 h-1.5 rounded-full transition-colors ${i === imgIndex ? "bg-white" : "bg-white/50"}`}
                    />
                  ))}
                </div>
              </>
            )}

            <button
              onClick={onClose}
              className="absolute top-4 right-4 z-10 w-8 h-8 rounded-full bg-white/90 flex items-center justify-center text-gray-500 hover:text-gray-700 shadow-sm"
            >
              <X className="w-4 h-4" />
            </button>
            {item.is_fully_reserved && (
              <div className="absolute inset-0 bg-white/60 backdrop-blur-xs flex items-center justify-center">
                <span className="flex items-center gap-2 bg-green-500 text-white text-sm font-bold px-4 py-2 rounded-full shadow-lg">
                  <CheckCircle className="w-4 h-4" />
                  Полностью забронировано
                </span>
              </div>
            )}
          </div>

          {/* Content */}
          <div className="p-6">
            <h2 className="text-xl font-bold text-gray-800 mb-1">{item.title}</h2>

            {item.description && (
              <p className="text-sm text-gray-500 mb-4">{item.description}</p>
            )}

            <div className="flex items-center gap-4 mb-4 flex-wrap">
              {item.price != null && (
                <span className="text-2xl font-bold gradient-text">
                  {Number(item.price).toLocaleString("ru-RU")} ₽
                </span>
              )}
              {item.url && (
                <a
                  href={item.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1.5 text-sm text-purple-600 hover:text-purple-700 font-medium"
                >
                  <ExternalLink className="w-4 h-4" />
                  Открыть товар
                </a>
              )}
            </div>

            {/* Collective gift progress */}
            {item.target_quantity > 1 && (
              <div className="mb-5 p-3 rounded-xl bg-purple-50">
                <div className="flex items-center justify-between text-xs text-gray-600 mb-2">
                  <span className="flex items-center gap-1">
                    <Users className="w-3.5 h-3.5" />
                    Коллективный подарок
                  </span>
                  <span className="font-semibold">
                    {item.reserved_count} из {item.target_quantity} слотов занято
                  </span>
                </div>
                <div className="h-2 bg-purple-100 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${progressPct}%` }}
                    transition={{ duration: 0.7, ease: "easeOut" }}
                    className="h-full bg-gradient-to-r from-purple-400 to-pink-400 rounded-full"
                  />
                </div>
              </div>
            )}

            {/* Reserve action */}
            {!item.is_fully_reserved && onReserve && !isLoggedIn ? (
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.97 }}
                onClick={handleReserve}
                className="btn-primary w-full justify-center py-3 text-base"
              >
                <LogIn className="w-5 h-5" />
                Войти и забронировать
              </motion.button>
            ) : !item.is_fully_reserved && onReserve ? (
              <div className="space-y-3">
                {item.target_quantity > 1 && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Сколько берёте? (доступно: {available})
                    </label>
                    <input
                      className="input-field"
                      type="number"
                      min={1}
                      max={available}
                      value={quantity}
                      onChange={(e) => setQuantity(Number(e.target.value))}
                    />
                  </div>
                )}
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.97 }}
                  onClick={handleReserve}
                  disabled={loading || quantity < 1 || quantity > available}
                  className="btn-primary w-full justify-center py-3 text-base"
                >
                  {loading ? (
                    "Бронируем..."
                  ) : (
                    <>
                      <Gift className="w-5 h-5" />
                      Забронировать подарок
                    </>
                  )}
                </motion.button>
              </div>
            ) : item.is_fully_reserved ? (
              <div className="flex items-center justify-center gap-2 py-3 rounded-xl bg-green-50 text-green-700 font-medium">
                <CheckCircle className="w-5 h-5" />
                Этот подарок уже забронирован
              </div>
            ) : null}
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
