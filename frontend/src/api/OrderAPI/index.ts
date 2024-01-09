import { ChildrenID } from 'api/ChildrenAPI/types'
import { CustomerID } from 'api/CustomerAPI/types'
import API from '..'
import {
	DiscountsResponse,
	OrderCreationPayload,
	OrderCreationResponse,
	OrderSummaryType,
	OrderType,
	ShippingRatesResponse
} from './types'

const BACKEND_URL = '/api'

export class OrderAPI extends API {
	async createOrder(payload: OrderCreationPayload): Promise<OrderCreationResponse> {
		return await this.client
			.post('/v1/orders/', this.createDTO(payload))
			.then((resp) => {
				return this._data(resp) as OrderCreationResponse
			})
	}

	async getLatestOrder(customer:CustomerID, customerChild: ChildrenID): Promise<OrderType> {
		return await this.client
			.get(`/v1/orders/latest/?customer=${customer}&customer_child=${customerChild}`)
			.then((resp)=>{
				return this._data(resp)
			})
	}

	async fetchOrderSummary(customerID: CustomerID, discountCode?: string): Promise<OrderSummaryType> {
		const discountCodeArg = discountCode ? `&discount=${discountCode}` : ''
		return await this.client
			.get(`/v1/orders/summary/?customer=${customerID}${discountCodeArg}`)
			.then((resp) => {
				return this._data(resp)
			})
	}

	async fetchShippingRates(): Promise<ShippingRatesResponse> {
		return await this.client
			.get('/v1/shipping_rates/')
			.then((resp) => {
				return this._data(resp) as ShippingRatesResponse
			})
	}

	async fetchDiscounts(): Promise<DiscountsResponse> {
		return await this.client
			.get('/v1/discounts/')
			.then((resp) => {
				return this._data(resp) as DiscountsResponse
			})
	}
}

export default new OrderAPI({
	baseURL: BACKEND_URL
})
