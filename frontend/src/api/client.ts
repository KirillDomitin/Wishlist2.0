import axios from "axios";

const client = axios.create({
  baseURL: "/api",
  headers: { "Cache-Control": "no-cache, no-store", Pragma: "no-cache" },
});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

let isRefreshing = false;
let queue: Array<(token: string) => void> = [];

function processQueue(newToken: string) {
  queue.forEach((resolve) => resolve(newToken));
  queue = [];
}

function forceLogout() {
  localStorage.removeItem("token");
  localStorage.removeItem("refresh_token");
  window.location.href = "/login";
}

client.interceptors.response.use(
  (res) => res,
  async (err) => {
    const original = err.config;

    // Not 401, or this is already a retry, or it's the refresh endpoint itself
    if (
      err.response?.status !== 401 ||
      original._retry ||
      original.url === "/users/refresh"
    ) {
      return Promise.reject(err);
    }

    const refreshToken = localStorage.getItem("refresh_token");
    if (!refreshToken) {
      forceLogout();
      return Promise.reject(err);
    }

    if (isRefreshing) {
      return new Promise((resolve) => {
        queue.push((token) => {
          original.headers.Authorization = `Bearer ${token}`;
          resolve(client(original));
        });
      });
    }

    original._retry = true;
    isRefreshing = true;

    try {
      const res = await client.post("/users/refresh", { refresh_token: refreshToken });
      const { access_token, refresh_token: newRefreshToken } = res.data;

      localStorage.setItem("token", access_token);
      localStorage.setItem("refresh_token", newRefreshToken);

      processQueue(access_token);
      original.headers.Authorization = `Bearer ${access_token}`;
      return client(original);
    } catch {
      queue = [];
      forceLogout();
      return Promise.reject(err);
    } finally {
      isRefreshing = false;
    }
  }
);

export default client;
