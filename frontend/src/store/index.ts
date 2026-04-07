import { configureStore } from "@reduxjs/toolkit";
import authReducer from "./authSlice";
import wishlistReducer from "./wishlistSlice";
import reservationReducer from "./reservationSlice";

export const store = configureStore({
  reducer: {
    auth: authReducer,
    wishlists: wishlistReducer,
    reservations: reservationReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
