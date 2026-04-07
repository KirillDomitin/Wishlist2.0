import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { reservationApi } from "../api/reservations";
import type { Reservation, ReservationCreate } from "../api/reservations";

interface ReservationState {
  list: Reservation[];
  loading: boolean;
  error: string | null;
}

const initialState: ReservationState = {
  list: [],
  loading: false,
  error: null,
};

export const fetchMyReservations = createAsyncThunk(
  "reservations/fetchMy",
  async () => reservationApi.listMy()
);

export const createReservation = createAsyncThunk(
  "reservations/create",
  async (data: ReservationCreate, { rejectWithValue }) => {
    try {
      return await reservationApi.create(data);
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } } };
      return rejectWithValue(err.response?.data?.detail ?? "Ошибка бронирования");
    }
  }
);

export const cancelReservation = createAsyncThunk(
  "reservations/cancel",
  async (id: string) => {
    await reservationApi.cancel(id);
    return id;
  }
);

const reservationSlice = createSlice({
  name: "reservations",
  initialState,
  reducers: {
    clearError(state) {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchMyReservations.pending, (state) => { state.loading = true; })
      .addCase(fetchMyReservations.fulfilled, (state, action) => {
        state.loading = false;
        state.list = action.payload;
      })
      .addCase(fetchMyReservations.rejected, (state) => { state.loading = false; })

      .addCase(createReservation.fulfilled, (state, action) => {
        state.list.push(action.payload);
      })
      .addCase(createReservation.rejected, (state, action) => {
        state.error = action.payload as string;
      })

      .addCase(cancelReservation.fulfilled, (state, action) => {
        const item = state.list.find((r) => r.id === action.payload);
        if (item) item.status = "cancelled";
      });
  },
});

export const { clearError } = reservationSlice.actions;
export default reservationSlice.reducer;
