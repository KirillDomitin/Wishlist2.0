import { useEffect, useRef, useState } from "react";
import { Modal } from "./ui/Modal";
import type { WishlistItem, WishlistItemCreate } from "../api/wishlists";
import { wishlistApi } from "../api/wishlists";

type ImageMode = "url" | "file" | "paste";

interface Props {
  open: boolean;
  onClose: () => void;
  editItem?: WishlistItem | null;
  onSubmit: (data: WishlistItemCreate) => Promise<void>;
}

interface PendingImage {
  preview: string;         // blob URL or final URL
  url: string;             // final URL (empty while uploading)
  uploading: boolean;
  promise: Promise<string> | null;
}

export function AddItemModal({ open, onClose, editItem, onSubmit }: Props) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [url, setUrl] = useState("");
  const [price, setPrice] = useState("");
  const [targetQty, setTargetQty] = useState("1");
  const [loading, setLoading] = useState(false);

  const [images, setImages] = useState<PendingImage[]>([]);
  const [imageMode, setImageMode] = useState<ImageMode>("url");
  const [urlInput, setUrlInput] = useState("");

  const fileInputRef = useRef<HTMLInputElement>(null);
  const imagesRef = useRef<PendingImage[]>(images);
  imagesRef.current = images; // always in sync, no stale closure

  useEffect(() => {
    if (editItem) {
      setTitle(editItem.title);
      setDescription(editItem.description ?? "");
      setUrl(editItem.url ?? "");
      setPrice(editItem.price != null ? String(editItem.price) : "");
      setTargetQty(String(editItem.target_quantity));
      setImages(
        (editItem.image_urls ?? []).map((u) => ({
          preview: u,
          url: u,
          uploading: false,
          promise: null,
        }))
      );
    } else {
      setTitle(""); setDescription(""); setUrl("");
      setPrice(""); setTargetQty("1"); setImages([]);
    }
    setImageMode("url");
    setUrlInput("");
  }, [editItem, open]);

  const addUploadedFile = async (file: File) => {
    const preview = URL.createObjectURL(file);
    const promise = wishlistApi.uploadImage(file);

    const pending: PendingImage = { preview, url: "", uploading: true, promise };
    setImages((prev) => [...prev, pending]);

    try {
      const uploadedUrl = await promise;
      setImages((prev) =>
        prev.map((img) =>
          img.promise === promise
            ? { ...img, url: uploadedUrl, preview: uploadedUrl, uploading: false, promise: null }
            : img
        )
      );
    } catch {
      setImages((prev) => prev.filter((img) => img.promise !== promise));
    }
  };

  const addUrlImage = () => {
    const trimmed = urlInput.trim();
    if (!trimmed) return;
    setImages((prev) => [
      ...prev,
      { preview: trimmed, url: trimmed, uploading: false, promise: null },
    ]);
    setUrlInput("");
  };

  const removeImage = (index: number) => {
    setImages((prev) => prev.filter((_, i) => i !== index));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files ?? []);
    files.forEach(addUploadedFile);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handlePaste = (e: React.ClipboardEvent) => {
    const items = Array.from(e.clipboardData.items).filter((i) =>
      i.type.startsWith("image/")
    );
    items.forEach((item) => {
      const file = item.getAsFile();
      if (file) addUploadedFile(file);
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    setLoading(true);

    const resolvedUrls = await Promise.all(
      imagesRef.current.map(async (img) => {
        if (img.promise) {
          try { return await img.promise; } catch { return null; }
        }
        return img.url || null;
      })
    );

    await onSubmit({
      title: title.trim(),
      description: description.trim() || undefined,
      url: url.trim() || undefined,
      price: price ? Number(price) : undefined,
      image_urls: resolvedUrls.filter((u): u is string => !!u),
      target_quantity: Number(targetQty) || 1,
    });
    setLoading(false);
    onClose();
  };

  const tabClass = (mode: ImageMode) =>
    `flex-1 py-1.5 text-xs font-medium transition-colors ${
      imageMode === mode
        ? "bg-indigo-600 text-white"
        : "text-gray-500 hover:text-gray-700"
    }`;

  const anyUploading = images.some((img) => img.uploading);

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={editItem ? "Редактировать желание" : "Добавить желание"}
    >
      <form onSubmit={handleSubmit} noValidate className="space-y-3">
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

        {/* Image section */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Картинки {images.length > 0 && <span className="text-gray-400 font-normal">({images.length})</span>}
          </label>

          {/* Existing images */}
          {images.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-2">
              {images.map((img, i) => (
                <div key={i} className="relative">
                  <img
                    src={img.preview}
                    alt=""
                    className="w-16 h-16 rounded-lg object-cover border border-gray-200"
                  />
                  {img.uploading && (
                    <div className="absolute inset-0 flex items-center justify-center rounded-lg bg-white/60">
                      <span className="text-[10px] text-gray-500">...</span>
                    </div>
                  )}
                  <button
                    type="button"
                    onClick={() => removeImage(i)}
                    className="absolute -top-1.5 -right-1.5 w-4 h-4 rounded-full bg-gray-600 text-white flex items-center justify-center text-[10px] leading-none hover:bg-red-500 transition-colors"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Mode tabs */}
          <div className="flex border border-gray-200 rounded-lg overflow-hidden mb-2">
            <button type="button" className={tabClass("url")} onClick={() => setImageMode("url")}>Ссылка</button>
            <button type="button" className={tabClass("file")} onClick={() => setImageMode("file")}>Файл</button>
            <button type="button" className={tabClass("paste")} onClick={() => setImageMode("paste")}>Буфер</button>
          </div>

          {/* URL mode */}
          {imageMode === "url" && (
            <div className="flex gap-2">
              <input
                className="input-field"
                type="url"
                placeholder="https://..."
                value={urlInput}
                onChange={(e) => setUrlInput(e.target.value)}
                onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); addUrlImage(); } }}
              />
              <button
                type="button"
                onClick={addUrlImage}
                disabled={!urlInput.trim()}
                className="btn-secondary shrink-0 px-3"
              >
                +
              </button>
            </div>
          )}

          {/* File mode */}
          {imageMode === "file" && (
            <>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                multiple
                className="hidden"
                onChange={handleFileChange}
              />
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="w-full h-16 border-2 border-dashed border-gray-300 rounded-lg flex flex-col items-center justify-center gap-1 text-gray-400 hover:border-indigo-400 hover:text-indigo-500 transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <span className="text-xs">Выбрать файлы (можно несколько)</span>
              </button>
            </>
          )}

          {/* Paste mode */}
          {imageMode === "paste" && (
            <div
              tabIndex={0}
              onPaste={handlePaste}
              className="w-full h-16 border-2 border-dashed border-gray-300 rounded-lg flex flex-col items-center justify-center gap-1 text-gray-400 hover:border-indigo-400 hover:text-indigo-500 transition-colors cursor-pointer focus:outline-none focus:border-indigo-400"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              <span className="text-xs">Кликните и нажмите Ctrl+V</span>
            </div>
          )}
        </div>

        <div className="flex gap-3 pt-2">
          <button type="button" onClick={onClose} className="btn-secondary flex-1">Отмена</button>
          <button type="submit" disabled={!title.trim() || loading} className="btn-primary flex-1">
            {loading ? (anyUploading ? "Загрузка..." : "Сохраняем...") : editItem ? "Сохранить" : "Добавить"}
          </button>
        </div>
      </form>
    </Modal>
  );
}
