import client from "./client";

export interface UserInfo {
  id: string;
  email: string;
  name: string;
  is_admin: boolean;
}

export interface UserUpdateRequest {
  name?: string;
  current_password?: string;
  new_password?: string;
}

export const usersApi = {
  getMe: async (): Promise<UserInfo> => {
    const res = await client.get<UserInfo>("/users/me");
    return res.data;
  },

  getById: async (userId: string): Promise<UserInfo> => {
    const res = await client.get<UserInfo>(`/users/${userId}`);
    return res.data;
  },

  updateMe: async (data: UserUpdateRequest): Promise<UserInfo> => {
    const res = await client.patch<UserInfo>("/users/me", data);
    return res.data;
  },
};
