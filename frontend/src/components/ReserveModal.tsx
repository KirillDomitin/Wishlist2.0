import { useState } from "react";
import { Modal } from "./ui/Modal";
import { Gift } from "lucide-react";
import type { WishlistItem } from "../api/wishlists";

interface Props {
  open: boolean;
  onClose: () => void;
  item: WishlistItem | null;
  onSubmit: (itemId: string, quantity: number) => Promise<void>;
}

export function ReserveModal({ open, onClose, item, onSubmit }: Props) {
  const [quantity, setQuantity] = useState(1);
  const [loading, setLoading] = useState(false);

  if (!item) return null;

  const available = item.target_quantity - item.reserved_count;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    await onSubmit(item.id, quantity);
    setLoading(false);
    setQuantity(1);
    onClose();
  };

  return (
    <Modal open={open} onClose={onClose} title="Забронировать подарок">
      <div className="mb-5 p-4 rounded-xl bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-100">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center">
            <Gift className="w-5 h-5 text-white" />
          </div>
          <div>
            <p className="font-semibold text-gray-800">{item.title}</p>
            {item.price != null && (
              <p className="text-sm text-purple-600 font-medium">
                {Number(item.price).toLocaleString("ru-RU")} ₽
              </p>
            )}
          </div>
        </div>
        {item.target_quantity > 1 && (
          <p className="text-xs text-gray-500 mt-2">
            Доступно слотов: <span className="font-semibold text-purple-600">{available}</span> из {item.target_quantity}
          </p>
        )}
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {item.target_quantity > 1 && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Сколько берёте?
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

        <div className="flex gap-3">
          <button type="button" onClick={onClose} className="btn-secondary flex-1">Отмена</button>
          <button type="submit" disabled={loading || quantity < 1 || quantity > available} className="btn-primary flex-1">
            {loading ? "Бронируем..." : "🎁 Забронировать"}
          </button>
        </div>
      </form>
    </Modal>
  );
}
