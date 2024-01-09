import { configureStore } from '@reduxjs/toolkit'

import subscription from './subscriptionSlice'
import ingredient from './ingredientSlice'
import carts from './cartSlice'
import errorHandler from './errorHandler'

const store = configureStore({
	reducer: {
		subscription,
		ingredient,
		carts,
	},
	middleware: (getDefaultMiddleware) => (
		getDefaultMiddleware().concat([errorHandler])
	),
	devTools: process.env.NODE_ENV !== 'production',
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch

export const dispatch = store.dispatch
export default store
