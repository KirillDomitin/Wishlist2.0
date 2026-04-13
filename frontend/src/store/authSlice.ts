import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { authApi } from "../api/auth";
import { usersApi } from "../api/users";

interface AuthState {
  token: string | null;
  name: string | null;
  loading: boolean;
  error: string | null;
}

const initialState: AuthState = {
  token: localStorage.getItem("token"),
  name: null,
  loading: false,
  error: null,
};

function saveTokens(access_token: string, refresh_token: string) {
  localStorage.setItem("token", access_token);
  localStorage.setItem("refresh_token", refresh_token);
}

export const fetchMe = createAsyncThunk("auth/fetchMe", async () => {
  const user = await usersApi.getMe();
  return user.name;
});

type ApiError = { response?: { data?: { detail?: string | Array<{ msg: string }> } } };

function extractErrorMessage(e: unknown, fallback: string): string {
  const detail = (e as ApiError).response?.data?.detail;
  if (!detail) return fallback;
  if (Array.isArray(detail)) return detail.map((d) => d.msg).join(", ");
  return detail;
}

export const login = createAsyncThunk(
  "auth/login",
  async (data: { email: string; password: string }, { rejectWithValue }) => {
    try {
      const res = await authApi.login(data);
      saveTokens(res.access_token, res.refresh_token);
      return res.access_token;
    } catch (e: unknown) {
      return rejectWithValue(extractErrorMessage(e, "Ошибка входа"));
    }
  }
);

// Returns void — registration now only sends a verification email
export const register = createAsyncThunk(
  "auth/register",
  async (
    data: { email: string; password: string; name: string },
    { rejectWithValue }
  ) => {
    try {
      await authApi.register(data);
    } catch (e: unknown) {
      return rejectWithValue(extractErrorMessage(e, "Ошибка регистрации"));
    }
  }
);

export const verifyEmail = createAsyncThunk(
  "auth/verifyEmail",
  async (data: { email: string; code: string }, { rejectWithValue }) => {
    try {
      const res = await authApi.verifyEmail(data);
      saveTokens(res.access_token, res.refresh_token);
      return res.access_token;
    } catch (e: unknown) {
      return rejectWithValue(extractErrorMessage(e, "Неверный код"));
    }
  }
);

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    logout(state) {
      const refreshToken = localStorage.getItem("refresh_token");
      if (refreshToken) {
        authApi.logout(refreshToken).catch(() => {});
      }
      state.token = null;
      state.name = null;
      localStorage.removeItem("token");
      localStorage.removeItem("refresh_token");
    },
    clearError(state) {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(login.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false;
        state.token = action.payload;
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      .addCase(fetchMe.fulfilled, (state, action) => {
        state.name = action.payload;
      })
      .addCase(register.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(register.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(register.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      .addCase(verifyEmail.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(verifyEmail.fulfilled, (state, action) => {
        state.loading = false;
        state.token = action.payload;
      })
      .addCase(verifyEmail.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { logout, clearError } = authSlice.actions;
export default authSlice.reducer;
