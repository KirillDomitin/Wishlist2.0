import client from "./client";

export interface ReservationItem {
  title: string;
  price: number | null;
  image_url: string | null;
  target_quantity: number;
}

export interface Reservation {
  id: string;
  item_id: string;
  reserver_id: string;
  quantity: number;
  status: "active" | "cancelled";
  item: ReservationItem | null;
}

export interface ReservationCreate {
  item_id: string;
  quantity: number;
}

export interface WishlistReservationInfo {
  item_id: string;
  reserver_id: string;
  quantity: number;
}

export const reservationApi = {
  listMy: async (): Promise<Reservation[]> => {
    const res = await client.get<Reservation[]>("/reservations/");
    return res.data;
  },

  listForWishlist: async (wishlistId: string): Promise<WishlistReservationInfo[]> => {
    const res = await client.get<WishlistReservationInfo[]>(`/reservations/wishlist/${wishlistId}`);
    return res.data;
  },

  create: async (data: ReservationCreate): Promise<Reservation> => {
    const res = await client.post<Reservation>("/reservations/", data);
    return res.data;
  },

  cancel: async (id: string): Promise<void> => {
    await client.delete(`/reservations/${id}`);
  },
};
