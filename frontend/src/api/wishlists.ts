import client from "./client";

export interface WishlistItem {
  id: string;
  title: string;
  description: string | null;
  url: string | null;
  price: number | null;
  image_urls: string[];
  target_quantity: number;
  reserved_count: number;
  is_fully_reserved: boolean;
  priority: number;
}

export interface WishlistSummary {
  id: string;
  title: string;
  share_token: string;
  surprise_mode: boolean;
  event_date: string | null;
  item_count: number;
}

export interface WishlistDetail {
  id: string;
  title: string;
  share_token: string;
  surprise_mode: boolean;
  event_date: string | null;
  items: WishlistItem[];
}

export interface WishlistCreate {
  title: string;
  surprise_mode?: boolean;
  event_date?: string | null;
}

export interface WishlistUpdate {
  title?: string;
  surprise_mode?: boolean;
  event_date?: string | null;
}

export interface WishlistItemCreate {
  title: string;
  description?: string;
  url?: string;
  price?: number;
  image_urls?: string[];
  target_quantity?: number;
  priority?: number;
}

export interface WishlistItemUpdate {
  title?: string;
  description?: string;
  url?: string;
  price?: number;
  image_urls?: string[];
  target_quantity?: number;
  priority?: number;
}

export const wishlistApi = {
  listMy: async (): Promise<WishlistSummary[]> => {
    const res = await client.get<WishlistSummary[]>("/wishlists/");
    return res.data;
  },

  getDetail: async (id: string): Promise<WishlistDetail> => {
    const res = await client.get<WishlistDetail>(`/wishlists/${id}`);
    return res.data;
  },

  getShared: async (token: string): Promise<WishlistDetail> => {
    const res = await client.get<WishlistDetail>(`/wishlists/shared/${token}`);
    return res.data;
  },

  create: async (data: WishlistCreate): Promise<WishlistSummary> => {
    const res = await client.post<WishlistSummary>("/wishlists/", data);
    return res.data;
  },

  update: async (id: string, data: WishlistUpdate): Promise<WishlistSummary> => {
    const res = await client.patch<WishlistSummary>(`/wishlists/${id}`, data);
    return res.data;
  },

  delete: async (id: string): Promise<void> => {
    await client.delete(`/wishlists/${id}`);
  },

  addItem: async (wishlistId: string, data: WishlistItemCreate): Promise<WishlistItem> => {
    const res = await client.post<WishlistItem>(`/wishlists/${wishlistId}/items`, data);
    return res.data;
  },

  updateItem: async (
    wishlistId: string,
    itemId: string,
    data: WishlistItemUpdate
  ): Promise<WishlistItem> => {
    const res = await client.patch<WishlistItem>(
      `/wishlists/${wishlistId}/items/${itemId}`,
      data
    );
    return res.data;
  },

  deleteItem: async (wishlistId: string, itemId: string): Promise<void> => {
    await client.delete(`/wishlists/${wishlistId}/items/${itemId}`);
  },

  uploadImage: async (file: File): Promise<string> => {
    const form = new FormData();
    form.append("file", file);
    const res = await client.post<{ url: string }>("/wishlists/upload-image", form);
    return res.data.url;
  },
};
