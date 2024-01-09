import {SubscriptionAPI} from './'
import mockAxios from 'src/__mocks__/axios'


class fakeClass extends SubscriptionAPI{

	getClient(){
		return this.client
	}
}

const api = new fakeClass({})


describe('Product API', ()=>{
	test('gets products succesfully', async ()=>{
		mockAxios.post.mockResolvedValueOnce([{
			customer: '123',
			customerChild: '12312',
			frequency: 12,
			numberOfServings: 24,
			isActive: false,
		}])
		const payload = {
			customer: '123',
			customerChild: '12312',
			frequency: 12,
			numberOfServings: 24
		}
		await api.createSubscription(payload)
		expect(api.getClient().post).toHaveBeenCalledWith(
			'/v1/customers-subscriptions/',
			{...payload}
		)

	})

	test('updateSubcriptionChargeDate: gets called with proper endpoint', async ()=>{
		mockAxios.patch.mockResolvedValueOnce({
			data: {}
		})
		const payload = {
			subscription: 'subscriptionid',
			nextOrderChargeDate: '2020-20-10'
		}
		await api.updateSubcriptionChargeDate(payload)
		expect(api.getClient().patch).toHaveBeenCalledWith(
			`/v1/customers-subscriptions/${payload.subscription}/`,
			{
				nextOrderChargeDate: payload.nextOrderChargeDate
			}
		)
	})

	test('cancelSubscription: gets called with proper endpoint', async ()=>{
		mockAxios.put.mockResolvedValueOnce({
			data: {}
		})
		const subscriptionId = 'subscription-id'
		await api.cancelSubscription(subscriptionId)
		expect(api.getClient().put).toHaveBeenCalledWith(
			`/v1/customers-subscriptions/${subscriptionId}/cancel/`,
		)
	})

	test('reactiveSubscription: gets called with proper endpoint', async ()=>{
		mockAxios.put.mockResolvedValueOnce({
			data: {}
		})
		const subscriptionId = 'subscription-id'
		await api.reactiveSubscription(subscriptionId)
		expect(api.getClient().put).toHaveBeenCalledWith(
			`/v1/customers-subscriptions/${subscriptionId}/reactivate/`,
		)
	})
})
