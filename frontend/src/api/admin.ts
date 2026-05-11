import client from "./client";

export interface AdminUser {
  id: string;
  email: string;
  name: string;
  is_admin: boolean;
  created_at: string;
}

export interface AdminWishlist {
  id: string;
  owner_id: string;
  title: string;
  is_public: boolean;
  surprise_mode: boolean;
  event_date: string | null;
  item_count: number;
  created_at: string;
}

export interface LogEntry {
  timestamp: string;
  level: string;
  service: string;
  logger: string;
  message: string;
}

export interface AdminUserUpdateRequest {
  name?: string;
  email?: string;
  is_admin?: boolean;
}

export interface AdminWishlistUpdateRequest {
  title?: string;
  is_public?: boolean;
  surprise_mode?: boolean;
  event_date?: string | null;
}

export const adminApi = {
  getUsers: () =>
    client.get<AdminUser[]>("/users/admin/users").then((r) => r.data),

  updateUser: (id: string, data: AdminUserUpdateRequest) =>
    client.patch<AdminUser>(`/users/admin/users/${id}`, data).then((r) => r.data),

  deleteUser: (id: string) =>
    client.delete(`/users/admin/users/${id}`),

  getWishlists: () =>
    client.get<AdminWishlist[]>("/wishlists/admin/wishlists").then((r) => r.data),

  updateWishlist: (id: string, data: AdminWishlistUpdateRequest) =>
    client.patch<AdminWishlist>(`/wishlists/admin/wishlists/${id}`, data).then((r) => r.data),

  getLogs: (params: { service?: string; level?: string; limit?: number }) =>
    client.get<LogEntry[]>("/users/admin/logs", { params }).then((r) => r.data),
};
