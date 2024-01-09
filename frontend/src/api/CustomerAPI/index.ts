import API from '..'
import {
	AddCustomerDetailsPayload,
	Customer,
	CustomerCreationPayload,
	CustomerUpdatePayload
} from './types'

const BACKEND_URL = '/api'

export class CustomerAPI extends API{

	/** move this logic to the backend */
	_data(res:any):any{
		const {data} = res
		if(!data.subscriptions){
			return super._data(res)
		}
		const subs:Record<any, any> = {}
		data.subscriptions.forEach((sub:any)=>{
			subs[sub.customerChild] = sub
		})

		data.subscriptions = subs
		return super._data(res)
	}

	async create(
		customer:CustomerCreationPayload
	): Promise<Customer>{
		return this.client
			.post('/v1/customers/', this.createDTO(customer))
			.then((resp)=>{
				return this._data(resp) as Customer
			})
	}

	async get(
		id?:string
	): Promise<Customer>{
		return this.client
			.get('v1/customers/current_user/')
			.then((resp)=>{
				return this._data(resp) as Customer
			})
	}

	async update(
		customer:CustomerUpdatePayload
	): Promise<Customer>{
		const {id, ..._customer} = customer
		return this.client
			.patch(`/v1/customers/${id}/`, this.createDTO(_customer))
			.then((resp)=>{
				return this._data(resp) as Customer
			})
	}

	/**
	 * Creates user password
	 * Only to be used when onboarding user for the first time
	 */
	async createCustomerPassword(
		{
			id,
			password
		}:AddCustomerDetailsPayload
	):Promise<void>{
		return this.client
			.post(`/v1/customers/${id}/set_password/`, this.createDTO({password}))
	}
}

// IAM API singleton
export default new CustomerAPI({
	baseURL: BACKEND_URL 
})
