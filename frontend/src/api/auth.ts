import client from "./client";

interface LoginRequest {
  email: string;
  password: string;
}

interface RegisterRequest {
  email: string;
  password: string;
  name: string;
}

interface TokenResponse {
  access_token: string;
}

export const authApi = {
  login: async (data: LoginRequest): Promise<TokenResponse> => {
    const res = await client.post<TokenResponse>("/users/login", data);
    return res.data;
  },

  register: async (data: RegisterRequest): Promise<TokenResponse> => {
    const res = await client.post<TokenResponse>("/users/register", data);
    return res.data;
  },
};
