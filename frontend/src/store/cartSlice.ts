import { createSlice, createAsyncThunk} from '@reduxjs/toolkit'
import { cloneDeep } from 'lodash'

import {
	APIstatus, BaseReducerStateAPI
} from './types'
import CartAPI from 'src/api/CartAPI'
import {CartType, CartUpdatePayload} from 'src/api/CartAPI/types'


export const initStore = createAsyncThunk(
	'cart/initStore',
	async (customerId: string, {rejectWithValue}) => {
		try {
			return await CartAPI.getChildrenCarts(customerId)
		} catch (err: any) {
			return rejectWithValue(
				err.message || 'There was an error in fetching your orders, please reload the page'
			)
		}
	}
)

export type CartSliceType = {
  customer: string,
  children: any,
}

export const getChildrenCarts = createAsyncThunk(
	'cart/getChildrenCarts',
	async (customerId: string, {rejectWithValue}) => {
		try {
			return await CartAPI.getChildrenCarts(customerId)
		} catch (err: any) {
			return rejectWithValue(
				err.message || 'There was an error in fetching the cart, please reload the page'
			)
		}
	}
)

export const updateCartLineItems = createAsyncThunk(
	'cart/updateCartLineItems',
	async (payload: CartUpdatePayload, {rejectWithValue}) => {
		try {			
			return await CartAPI.updateCartLineItems(payload)
		} catch (err: any) {
			return rejectWithValue(
				err.message ||
					'There was an error updating the cart, please try again'
			)
		}
	}
)

export interface CartSliceState extends CartSliceType, BaseReducerStateAPI {}

export const initialState:CartSliceState = {
	init: false,
	APIStatus: APIstatus.idle,
	error: '',
	customer: '',
	children: {},
}

export const cartSlice = createSlice({
	name: 'carts',
	initialState: cloneDeep(initialState),
	reducers: {
		resetStore(state){
			Object.assign(state, cloneDeep(initialState))
		}
	},
	extraReducers: (builders) => {
		builders.addCase(initStore.rejected, (state, action) => {
			state.error = action.error.message
			state.init = true
			state.APIStatus = APIstatus.error
		})
		builders.addCase(initStore.fulfilled, (state, action) => {
			const fetchedCarts = action.payload as Array<CartType> || []
			fetchedCarts.forEach((cart) => {
				state.children[cart.child] = {cartId: cart.id, id: cart.child, lineItems: cart.lineItems}
			})
			state.init = true
			state.APIStatus = APIstatus.success
		})

		builders.addCase(getChildrenCarts.pending, (state) => {
			state.APIStatus = APIstatus.loading
			state.error = ''
		})
		builders.addCase(getChildrenCarts.rejected, (state, action) => {
			state.APIStatus = APIstatus.error
			state.error = action.error.message
		})
		builders.addCase(getChildrenCarts.fulfilled, (state, action) => {
			// eslint-disable-next-line no-debugger
			const fetchedCarts = action.payload as Array<CartType> || []
			fetchedCarts.forEach((cart) => {
				state.children[cart.child] = {cartId: cart.id, id: cart.child, lineItems: cart.lineItems}
			})
			state.init = true
			state.APIStatus = APIstatus.success
		})

		builders.addCase(updateCartLineItems.pending, (state) => {
			state.APIStatus = APIstatus.loading
		})
		builders.addCase(updateCartLineItems.rejected, (state, action) => {
			state.APIStatus = APIstatus.error
			state.error = action.error.message
		})
		builders.addCase(updateCartLineItems.fulfilled, (state, action) => {
			const cart = action.payload as CartType
			state.children[cart.child] = {cartId: cart.id, id: cart.child, lineItems: cart.lineItems,}
			state.APIStatus = APIstatus.success
		})
	}
})

export const { resetStore } = cartSlice.actions
export default cartSlice.reducer
