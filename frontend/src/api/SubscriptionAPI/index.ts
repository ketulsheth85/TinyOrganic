import API from '..'
import { CreateCustomerSubscriptionPayload,
	CustomerPrecancelURL,
	CustomerSubscription, CustomerSubscriptionCreationResponse, UpdateCustomerSubscriptionChargeDatePayload
} from './types'

const BACKEND_URL = '/api'

export class SubscriptionAPI extends API {
	async createSubscription(payload: CreateCustomerSubscriptionPayload)
	:Promise<CustomerSubscriptionCreationResponse>{
		return this.client.post('/v1/customers-subscriptions/', payload)
			.then((resp)=>{
				return {...this._data(resp), isNew: resp.status === 201}
			})
	}

	async updateSubcriptionChargeDate({subscription, nextOrderChargeDate}: UpdateCustomerSubscriptionChargeDatePayload)
	:Promise<CustomerSubscription>{
		return this.client.patch(`/v1/customers-subscriptions/${subscription}/`, {nextOrderChargeDate})
			.then((resp)=>{
				return this._data(resp)
			})
	}

	async cancelSubscription(subscription: string): Promise<CustomerSubscription>{
		return this.client.put(`/v1/customers-subscriptions/${subscription}/cancel/`)
			.then((resp)=>{
				return this._data(resp)
			})
	}

	async precancelSubscription(subscription: string): Promise<CustomerPrecancelURL>{
		return this.client.get(`/v1/customers-subscriptions/${subscription}/precancel/`)
			.then((resp)=>{
				return this._data(resp)
			})
	}

	async reactiveSubscription(subscription: string): Promise<CustomerSubscription>{
		return this.client.put(`/v1/customers-subscriptions/${subscription}/reactivate/`)
			.then((resp)=>{
				return this._data(resp)
			})
	}
}

export default new SubscriptionAPI({
	baseURL: BACKEND_URL
})
