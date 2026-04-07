import client from "./client";

export interface UserInfo {
  id: string;
  email: string;
  name: string;
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
};
