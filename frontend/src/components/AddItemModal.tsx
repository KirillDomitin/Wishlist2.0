import { useEffect, useState } from "react";
import { Modal } from "./ui/Modal";
import type { WishlistItem, WishlistItemCreate } from "../api/wishlists";

interface Props {
  open: boolean;
  onClose: () => void;
  editItem?: WishlistItem | null;
  onSubmit: (data: WishlistItemCreate) => Promise<void>;
}

export function AddItemModal({ open, onClose, editItem, onSubmit }: Props) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [url, setUrl] = useState("");
  const [price, setPrice] = useState("");
  const [imageUrl, setImageUrl] = useState("");
  const [targetQty, setTargetQty] = useState("1");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (editItem) {
      setTitle(editItem.title);
      setDescription(editItem.description ?? "");
      setUrl(editItem.url ?? "");
      setPrice(editItem.price != null ? String(editItem.price) : "");
      setImageUrl(editItem.image_url ?? "");
      setTargetQty(String(editItem.target_quantity));
    } else {
      setTitle(""); setDescription(""); setUrl("");
      setPrice(""); setImageUrl(""); setTargetQty("1");
    }
  }, [editItem, open]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    setLoading(true);
    await onSubmit({
      title: title.trim(),
      description: description.trim() || undefined,
      url: url.trim() || undefined,
      price: price ? Number(price) : undefined,
      image_url: imageUrl.trim() || undefined,
      target_quantity: Number(targetQty) || 1,
    });
    setLoading(false);
    onClose();
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={editItem ? "Редактировать желание" : "Добавить желание"}
    >
      <form onSubmit={handleSubmit} className="space-y-3">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Название *</label>
          <input className="input-field" placeholder="Наушники Sony WH-1000XM5" value={title} onChange={(e) => setTitle(e.target.value)} autoFocus />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Описание</label>
          <textarea className="input-field resize-none h-16" placeholder="Цвет: чёрный, версия 2024..." value={description} onChange={(e) => setDescription(e.target.value)} />
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Цена (₽)</label>
            <input className="input-field" type="number" min="0" placeholder="25000" value={price} onChange={(e) => setPrice(e.target.value)} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Кол-во нужных</label>
            <input className="input-field" type="number" min="1" value={targetQty} onChange={(e) => setTargetQty(e.target.value)} />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Ссылка на товар</label>
          <input className="input-field" type="url" placeholder="https://..." value={url} onChange={(e) => setUrl(e.target.value)} />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">URL картинки</label>
          <input className="input-field" type="url" placeholder="https://..." value={imageUrl} onChange={(e) => setImageUrl(e.target.value)} />
        </div>

        <div className="flex gap-3 pt-2">
          <button type="button" onClick={onClose} className="btn-secondary flex-1">Отмена</button>
          <button type="submit" disabled={!title.trim() || loading} className="btn-primary flex-1">
            {loading ? "Сохраняем..." : editItem ? "Сохранить" : "Добавить"}
          </button>
        </div>
      </form>
    </Modal>
  );
}
