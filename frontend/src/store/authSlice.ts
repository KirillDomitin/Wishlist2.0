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

export const fetchMe = createAsyncThunk("auth/fetchMe", async () => {
  const user = await usersApi.getMe();
  return user.name;
});

export const login = createAsyncThunk(
  "auth/login",
  async (data: { email: string; password: string }, { rejectWithValue }) => {
    try {
      const res = await authApi.login(data);
      return res.access_token;
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } } };
      return rejectWithValue(err.response?.data?.detail ?? "Ошибка входа");
    }
  }
);

export const register = createAsyncThunk(
  "auth/register",
  async (
    data: { email: string; password: string; name: string },
    { rejectWithValue }
  ) => {
    try {
      const res = await authApi.register(data);
      return res.access_token;
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } } };
      return rejectWithValue(
        err.response?.data?.detail ?? "Ошибка регистрации"
      );
    }
  }
);

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    logout(state) {
      state.token = null;
      state.name = null;
      localStorage.removeItem("token");
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
        localStorage.setItem("token", action.payload);
      })
      .addCase(fetchMe.fulfilled, (state, action) => {
        state.name = action.payload;
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      .addCase(register.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(register.fulfilled, (state, action) => {
        state.loading = false;
        state.token = action.payload;
        localStorage.setItem("token", action.payload);
      })
      .addCase(register.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { logout, clearError } = authSlice.actions;
export default authSlice.reducer;
