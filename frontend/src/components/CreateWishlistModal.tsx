import { useState } from "react";
import { Modal } from "./ui/Modal";
import { EyeOff } from "lucide-react";

interface Props {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: {
    title: string;
    surprise_mode: boolean;
  }) => Promise<void>;
}

export function CreateWishlistModal({ open, onClose, onSubmit }: Props) {
  const [title, setTitle] = useState("");
  const [surpriseMode, setSurpriseMode] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    setLoading(true);
    await onSubmit({ title: title.trim(), surprise_mode: surpriseMode });
    setLoading(false);
    setTitle("");
    onClose();
  };

  return (
    <Modal open={open} onClose={onClose} title="Новый список желаний">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">
            Название списка
          </label>
          <input
            className="input-field"
            placeholder="Мой список на день рождения"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            autoFocus
          />
        </div>

        <div className="flex flex-col gap-3">
          <label className="flex items-center justify-between p-3 rounded-xl bg-amber-50 cursor-pointer">
            <div>
              <div className="flex items-center gap-1.5">
                <EyeOff className="w-4 h-4 text-amber-600" />
                <p className="text-sm font-medium text-gray-700">Режим сюрприза</p>
              </div>
              <p className="text-xs text-gray-500">Вы не видите, кто что забронировал</p>
            </div>
            <div
              onClick={() => setSurpriseMode(!surpriseMode)}
              className={`w-11 h-6 rounded-full transition-colors relative ${
                surpriseMode ? "bg-amber-500" : "bg-gray-200"
              }`}
            >
              <div
                className={`absolute top-1 w-4 h-4 bg-white rounded-full shadow transition-transform ${
                  surpriseMode ? "translate-x-6" : "translate-x-1"
                }`}
              />
            </div>
          </label>
        </div>

        <div className="flex gap-3 pt-2">
          <button type="button" onClick={onClose} className="btn-secondary flex-1">
            Отмена
          </button>
          <button type="submit" disabled={!title.trim() || loading} className="btn-primary flex-1">
            {loading ? "Создаём..." : "Создать"}
          </button>
        </div>
      </form>
    </Modal>
  );
}
