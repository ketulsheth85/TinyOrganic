import analyticsClient from 'src/libs/analytics'
import API from '..'

import {
	CustomerAddress,
	CustomerAddressCreationPayload,
	CustomerAddressUpdatePayload,
} from './types'

const BACKEND_URL = process.env.BACKEND_URL
export class AddressAPI extends API{

	async create(data: CustomerAddressCreationPayload): Promise<CustomerAddress>{
		const {firstName,lastName,email, ..._data} = data

		await analyticsClient.addedAddress({
			first_name: firstName,
			last_name: lastName,
			email,
			zipcode: _data.zipcode 
		})
		
		return this.client
			.post('/api/v1/addresses/', this.createDTO(_data))
			.then((res) => this._data(res) as (CustomerAddress))
	}

	async update(data: CustomerAddressUpdatePayload): Promise<CustomerAddress>{
		// eslint-disable-next-line @typescript-eslint/no-unused-vars
		const {id,firstName,lastName,email, ..._data} = data

		await analyticsClient.addedAddress({
			first_name: firstName,
			last_name: lastName,
			email,
			zipcode: _data.zipcode 
		})

		return this.client
			.put(`/api/v1/addresses/${id}/`, this.createDTO(_data))
			.then((res) => this._data(res) as (CustomerAddress))
	}
}

// AddressAPI singleton
export default new AddressAPI({
	baseURL: BACKEND_URL 
})
