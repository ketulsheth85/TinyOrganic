import API from '..'

import {
	CartType, CartUpdatePayload
} from 'api/CartAPI/types'

const BACKEND_URL = '/api'
export class CartAPI extends API {
	async getChildrenCarts(
		customerId: string
	): Promise<Array<CartType>>{
		return await this.client
			.get(`/v1/carts/?customer=${customerId}`)
			.then((resp: any) => {
				return resp.data as Array<CartType>
			})
	}

	async updateCartLineItems(
		payload: CartUpdatePayload
	): Promise<CartType> {
		return await this.client
			.patch(`/v1/carts/${payload.cartId}/?customer=${payload.customerId}`, {lineItems: payload.lineItems})
			.then((resp: any) => {
				return resp.data as CartType
			})
	}
}
// Cart API singleton
export default new CartAPI({
	baseURL: BACKEND_URL 
})
