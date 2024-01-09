import { AddressAPI } from '.'
import mockAxios from 'src/__mocks__/axios'
import { CustomerAddress } from './types'

class fakeClass extends AddressAPI{

	_createDTO(data:Partial<CustomerAddress>){
		return this.createDTO(data)
	}
}

const api = new fakeClass({})


describe('address api', ()=>{
	test('createDTO', ()=>{
		const address = {
			customer: 'customer-id',
			streetAddress: '12345',
			zipcode: '12345',
			city: 'city',
			isActive: false
		}

		expect(api._createDTO(address)).toMatchObject({
			customer: 'customer-id',
			streetAddress: '12345',
			zipcode: '12345',
			city: 'city',
			isActive: false
		})
	})

	test('create', async ()=>{
		const address = {
			customer: 'customer-id',
			streetAddress: '12345',
			zipcode: '12345',
			state: 'fl',
			city: 'city',
			isActive: false,
			firstName: '',
			lastName: '',
			email: ''
		}

		mockAxios.post.mockResolvedValue({
			customer: 'customer-id',
			streetAddress: '12345',
			state: 'fl',
			zipcode: '12345',
			city: 'city',
			isActive: false
		})

		await api.create(address)

		expect(mockAxios.post).toHaveBeenCalledWith(
			'/api/v1/addresses/',
			{
				customer: 'customer-id',
				streetAddress: '12345',
				state: 'fl',
				zipcode: '12345',
				city: 'city',
				isActive: false,
			},
		)
	})

	test('update', async ()=>{
		const address = {
			id: 'id',
			customer: 'customer-id',
			streetAddress: '12345',
			state: 'fl',
			zipcode: '12345',
			city: 'city',
			isActive: false,
			firstName: '',
			lastName: '',
			email: ''
		}

		mockAxios.put.mockResolvedValue({
			id: 'id',
			customer: 'customer-id',
			streetAddress: '12345',
			state: 'fl',
			zipcode: '12345',
			city: 'city',
			isActive: false,
			
		})

		await api.update(address)

		expect(mockAxios.put).toHaveBeenCalledWith(
			'/api/v1/addresses/id/',
			{
				customer: 'customer-id',
				streetAddress: '12345',
				state: 'fl',
				zipcode: '12345',
				city: 'city',
				isActive: false,
			},
		)
	})
})
