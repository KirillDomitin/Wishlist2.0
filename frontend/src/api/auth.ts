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

interface VerifyEmailRequest {
  email: string;
  code: string;
}

export interface RegisterInitiateResponse {
  message: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
}

export const authApi = {
  login: async (data: LoginRequest): Promise<TokenResponse> => {
    const res = await client.post<TokenResponse>("/users/login", data);
    return res.data;
  },

  register: async (data: RegisterRequest): Promise<RegisterInitiateResponse> => {
    const res = await client.post<RegisterInitiateResponse>("/users/register", data);
    return res.data;
  },

  verifyEmail: async (data: VerifyEmailRequest): Promise<TokenResponse> => {
    const res = await client.post<TokenResponse>("/users/verify-email", data);
    return res.data;
  },

  refresh: async (refresh_token: string): Promise<TokenResponse> => {
    const res = await client.post<TokenResponse>("/users/refresh", { refresh_token });
    return res.data;
  },

  logout: async (refresh_token: string): Promise<void> => {
    await client.post("/users/logout", { refresh_token });
  },
};
