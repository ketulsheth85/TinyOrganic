import { CustomerID } from 'api/CustomerAPI/types'
import API from '..'
import { 
	CreateChargePayload,
	CreatePaymentMethodPayload,
	CreatePaymentIntentPayload,
	PaymentIntentResponse, 
	Charge,
	PaymentMethod,
	CreateCustomerDiscountPayload
} from './types'

const BACKEND_URL = '/api'
export class BillingAPI extends API{

	async createPaymentIntent(payload:CreatePaymentIntentPayload):Promise<PaymentIntentResponse>{
		return await this.client
			.post('/v1/payment-intent/', this.createDTO(payload))
			.then((resp)=>{
				return this._data(resp) as PaymentIntentResponse
			})
	}

	/**
	 * You must include either payment_id or every other
	 * fields or all the fields in the CreateChargePayload
	 */
	async createCharge(payload: CreateChargePayload):Promise<Charge>{
		return await this.client
			.post('/v1/charge/', this.createDTO(payload))
			.then((resp)=>{
				return this._data(resp) as Charge
			})
	}

	/**
	 * You must include either payment_id or every other
	 * fields or all the fields in the CreatePaymentMethodPayload
	 */
	async createPaymentMethod(payload:CreatePaymentMethodPayload): Promise<PaymentMethod>{
		return await this.client
			.post('/v1/payment-method/', this.createDTO(payload))
			.then((resp)=>{
				return this._data(resp) as PaymentMethod
			})
	}

	async getLatestPaymentMethod(customer: CustomerID): 
	Promise<Pick<PaymentMethod, 'id'| 'customer' | 'lastFour' | 'expirationDate'>>{
		return await this.client
			.get(`/v1/payment-method/latest/?customer=${customer}`)
			.then((resp)=>{
				const data = this._data(resp)
				return data as Pick<PaymentMethod, 'id'| 'customer' | 'lastFour' | 'expirationDate'>
			})
	}

	async applyDiscountCode(payload: CreateCustomerDiscountPayload): Promise<any>{
		return await this.client
			.post('/v1/customer_discounts/', payload)
			.then((resp)=>{
				const data = this._data(resp)
				return data
			})
	}
}

// Billing API singleton
export default new BillingAPI({
	baseURL: BACKEND_URL 
})
