import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { wishlistApi } from "../api/wishlists";
import type {
  WishlistDetail,
  WishlistSummary,
  WishlistCreate,
  WishlistUpdate,
  WishlistItemCreate,
  WishlistItemUpdate,
} from "../api/wishlists";

interface WishlistState {
  list: WishlistSummary[];
  current: WishlistDetail | null;
  shared: WishlistDetail | null;
  loading: boolean;
  error: string | null;
}

const initialState: WishlistState = {
  list: [],
  current: null,
  shared: null,
  loading: false,
  error: null,
};

export const fetchMyWishlists = createAsyncThunk("wishlists/fetchMy", async () => {
  return wishlistApi.listMy();
});

export const fetchWishlistDetail = createAsyncThunk(
  "wishlists/fetchDetail",
  async (id: string) => wishlistApi.getDetail(id)
);

export const fetchSharedWishlist = createAsyncThunk(
  "wishlists/fetchShared",
  async (token: string) => wishlistApi.getShared(token)
);

export const createWishlist = createAsyncThunk(
  "wishlists/create",
  async (data: WishlistCreate) => wishlistApi.create(data)
);

export const updateWishlist = createAsyncThunk(
  "wishlists/update",
  async ({ id, data }: { id: string; data: WishlistUpdate }) =>
    wishlistApi.update(id, data)
);

export const deleteWishlist = createAsyncThunk(
  "wishlists/delete",
  async (id: string) => {
    await wishlistApi.delete(id);
    return id;
  }
);

export const addItem = createAsyncThunk(
  "wishlists/addItem",
  async ({ wishlistId, data }: { wishlistId: string; data: WishlistItemCreate }) =>
    wishlistApi.addItem(wishlistId, data)
);

export const updateItem = createAsyncThunk(
  "wishlists/updateItem",
  async ({
    wishlistId,
    itemId,
    data,
  }: {
    wishlistId: string;
    itemId: string;
    data: WishlistItemUpdate;
  }) => wishlistApi.updateItem(wishlistId, itemId, data)
);

export const deleteItem = createAsyncThunk(
  "wishlists/deleteItem",
  async ({ wishlistId, itemId }: { wishlistId: string; itemId: string }) => {
    await wishlistApi.deleteItem(wishlistId, itemId);
    return itemId;
  }
);

const wishlistSlice = createSlice({
  name: "wishlists",
  initialState,
  reducers: {
    clearCurrent(state) {
      state.current = null;
    },
    clearShared(state) {
      state.shared = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchMyWishlists.pending, (state) => { state.loading = true; })
      .addCase(fetchMyWishlists.fulfilled, (state, action) => {
        state.loading = false;
        state.list = action.payload;
      })
      .addCase(fetchMyWishlists.rejected, (state) => { state.loading = false; })

      .addCase(fetchWishlistDetail.pending, (state) => { state.loading = true; })
      .addCase(fetchWishlistDetail.fulfilled, (state, action) => {
        state.loading = false;
        state.current = action.payload;
      })
      .addCase(fetchWishlistDetail.rejected, (state) => { state.loading = false; })

      .addCase(fetchSharedWishlist.pending, (state) => { state.loading = true; })
      .addCase(fetchSharedWishlist.fulfilled, (state, action) => {
        state.loading = false;
        state.shared = action.payload;
      })
      .addCase(fetchSharedWishlist.rejected, (state) => { state.loading = false; })

      .addCase(createWishlist.fulfilled, (state, action) => {
        state.list.unshift(action.payload);
      })

      .addCase(updateWishlist.fulfilled, (state, action) => {
        const idx = state.list.findIndex((w) => w.id === action.payload.id);
        if (idx !== -1) state.list[idx] = action.payload;
        if (state.current?.id === action.payload.id) {
          state.current = { ...state.current, ...action.payload };
        }
      })

      .addCase(deleteWishlist.fulfilled, (state, action) => {
        state.list = state.list.filter((w) => w.id !== action.payload);
      })

      .addCase(addItem.fulfilled, (state, action) => {
        if (state.current) state.current.items.push(action.payload);
      })

      .addCase(updateItem.fulfilled, (state, action) => {
        if (state.current) {
          const idx = state.current.items.findIndex(
            (i) => i.id === action.payload.id
          );
          if (idx !== -1) state.current.items[idx] = action.payload;
        }
      })

      .addCase(deleteItem.fulfilled, (state, action) => {
        if (state.current) {
          state.current.items = state.current.items.filter(
            (i) => i.id !== action.payload
          );
        }
      });
  },
});

export const { clearCurrent, clearShared } = wishlistSlice.actions;
export default wishlistSlice.reducer;
