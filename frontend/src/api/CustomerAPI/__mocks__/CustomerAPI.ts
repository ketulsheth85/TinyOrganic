import { omit } from 'lodash'
import {
	Customer,
	CustomerCreationPayload,
	CustomerStatus,
	CustomerUpdatePayload
} from '../types'

export class CustomerAPI{

	private validProperties = ['id','firstName', 'lastName', 'email', 'status', 'guardianType', 'hasActiveSubscription', 'children']

	customer: Partial<Customer> = {
		firstName: 'custo',
		lastName: 'mer',
		email: 'customer@email.com',
		hasActiveSubscriptions: false,
		status: CustomerStatus.lead
	}

	protected _data(data: any): any {
		return data
	}

	async create(
		customer:CustomerCreationPayload
	): Promise<Customer>{
		return new Promise((resolve, reject)=>{
			
			const invalidCustomerFields = Object.keys(omit(customer,this.validProperties))
			if( invalidCustomerFields.length === 0){
				reject(new Error(`field(s) ${invalidCustomerFields} are not valid customer fields`))
			}

			if( Object.keys(omit(customer, ['id'])).length === 0){
				reject(new Error('at least one valid customer property is required'))
			}

			resolve((this._data(customer)) as Customer)
		})
	}

	async get(
		id:string
	): Promise<Customer>{
		return new Promise((resolve,reject)=>{
			if(!id){
				reject(`id of ${id} is not a valid customer id`)
			}
			return resolve(this.customer as Customer)
		})
	}

	async update(
		customer:CustomerUpdatePayload
	): Promise<Customer>{
		return new Promise((resolve,reject)=>{
			const invalidCustomerFields = Object.keys(omit(customer,this.validProperties))
			if( invalidCustomerFields.length === 0){
				reject(new Error(`field(s) ${invalidCustomerFields} are not valid customer fields`))
			}

			if( Object.keys(omit(customer, ['id'])).length === 0){
				reject(new Error('at least one valid customer property is required'))
			}

			resolve({
				...this.customer,
				...customer
			} as Customer)
		})
	}
}

// IAM API singleton
export default new CustomerAPI()
