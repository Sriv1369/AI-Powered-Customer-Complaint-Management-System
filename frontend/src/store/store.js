import { configureStore } from '@reduxjs/toolkit';
import complaintsReducer from './complaintSlice';

export const store = configureStore({
  reducer: {
    complaints: complaintsReducer
  }
});
