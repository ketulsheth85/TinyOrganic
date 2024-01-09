import mockAxios from 'src/__mocks__/axios'

import {OrderAPI} from './'

class API extends OrderAPI {
	getClient() {
		return this.client
	}
}

const api = new API({})

describe('Order API', () => {
	const order = {
		customer: 'customerID',
		carts: ['cartId1',]
	}
	beforeEach(()=>{
		jest.resetAllMocks()
	})
	describe('createOrder', ()=>{
		test('Gets calld with right endpoint and payload', async () => {
			mockAxios.post.mockResolvedValueOnce({
				data: order
			})
	
			await api.createOrder({
				customer: 'customerID',
				carts: ['cartId1',]
			})
	
			expect(api.getClient().post).toHaveBeenCalledWith(
				'/v1/orders/',
				order,
			)
		})
	})
	describe('fetchOrderSummary', ()=>{
		test('Gets called with customer arg', async () => {
			mockAxios.get.mockResolvedValueOnce({
				data: {}
			})
	
			await api.fetchOrderSummary('customerID')
	
			expect(api.getClient().get).toHaveBeenCalledWith(
				'/v1/orders/summary/?customer=customerID')
		})
		test('Gets called with customer and discount code args', async () => {
			mockAxios.get.mockResolvedValueOnce({
				data: {}
			})
	
			await api.fetchOrderSummary('customerID','DISCOUNT')
	
			expect(api.getClient().get).toHaveBeenCalledWith(
				'/v1/orders/summary/?customer=customerID&discount=DISCOUNT')
		})
	})

	describe('fetchShippingRates', ()=>{
		test('Gets called with expected endopoint', async () => {
			mockAxios.get.mockResolvedValueOnce({
				data: {}
			})
	
			await api.fetchShippingRates()
	
			expect(api.getClient().get).toHaveBeenCalledWith(
				'/v1/shipping_rates/')
		})
	})

	describe('fetchDiscounts', ()=>{
		test('Gets called with expected endopoint', async () => {
			mockAxios.get.mockResolvedValueOnce({
				data: {}
			})
	
			await api.fetchDiscounts()
	
			expect(api.getClient().get).toHaveBeenCalledWith(
				'/v1/discounts/')
		})
	})

	describe('getLatestOrder', ()=>{
		test('Gets called with expected endopoint', async () => {
			mockAxios.get.mockResolvedValueOnce({
				data: {}
			})
	
			await api.getLatestOrder('customerid', 'customerchildid')
	
			expect(api.getClient().get).toHaveBeenCalledWith(
				'/v1/orders/latest/?customer=customerid&customer_child=customerchildid')
		})
	})

})
