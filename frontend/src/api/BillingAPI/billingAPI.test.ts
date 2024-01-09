import mockAxios from 'src/__mocks__/axios'

import {BillingAPI} from './'

class API extends BillingAPI{
	getClient(){
		return this.client
	}
}

const api = new API({})

describe('Billing API', ()=>{
	const paymentIntent = {
		intent: 'abc123'
	}

	beforeEach(()=>{
		jest.resetAllMocks()
	})

	test('createPaymentIntent', async ()=>{
		mockAxios.post.mockResolvedValueOnce({
			data: paymentIntent
		})

		await api.createPaymentIntent({
			customer: '12345',
			items: [{id: '1234'}]
		})
		expect(api.getClient().post).toHaveBeenCalledWith(
			'/v1/payment-intent/',
			{
				customer: '12345',
				items: [{id: '1234'}]
			}
		)

	})

	test('createCharge', async ()=>{
		mockAxios.post.mockResolvedValueOnce({
			data: paymentIntent
		})

		await api.createCharge({
			customer: '1234',
			paymentCustomer: '12345',
			paymentMethod: 'someid',
			amount: 100
		})

		expect(api.getClient().post).toHaveBeenCalledWith(
			'/v1/charge/',
			{
				customer: '1234',
				paymentCustomer: '12345',
				paymentMethod: 'someid',
				amount: 100
			}
		)
	})

	test('createPaymentMethod', async ()=>{
		mockAxios.post.mockResolvedValueOnce({
			data: paymentIntent
		})

		await api.createPaymentMethod({
			paymentCustomer: 'stripe_id_maybe',
			customer: '12345',
			paymentMethod: 'someid',
		})

		expect(api.getClient().post).toHaveBeenCalledWith(
			'/v1/payment-method/',
			{
				paymentCustomer: 'stripe_id_maybe',
				customer: '12345',
				paymentMethod: 'someid',
			}
		)
	})

	test('getLatestPaymentMethod', async ()=>{
		mockAxios.get.mockResolvedValueOnce({
			data: {
				id: 'id',
				customer: 'customer',
				lastFour: 1234,
				expirationDate: '10/20'
			}
		})

		await api.getLatestPaymentMethod('customer')

		expect(api.getClient().get).toHaveBeenCalledWith(
			'/v1/payment-method/latest/?customer=customer',
		)
	})
})
