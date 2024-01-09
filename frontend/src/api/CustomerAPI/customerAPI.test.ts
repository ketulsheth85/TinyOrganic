import {CustomerAPI} from './'
import mockAxios from 'src/__mocks__/axios'

class fakeClass extends CustomerAPI{
	
}

const api = new fakeClass({})

describe('CustomerAPI', ()=>{
	test('create', async ()=>{
		const customer = {
			firstName: 'Steve',
			lastName: 'O',
			email: 'steveo@jackdonkey.com'
		}

		mockAxios.post.mockResolvedValue({
			data: {
				id: 'cool-guy',
				firstName: 'steve',
				lastName: 'o',
				email: 'steveo@jackdonkey.com',
				type: 'lead',
				guardianType: 'parent'
			}
		})

		const newCustomer = await api.create(customer)
		expect(mockAxios.post).toHaveBeenCalledWith('/v1/customers/',{
			firstName: 'Steve',
			lastName: 'O',
			email: 'steveo@jackdonkey.com',
		})

		expect(newCustomer).toMatchObject({
			id: 'cool-guy',
			firstName: 'steve',
			lastName: 'o',
			email: 'steveo@jackdonkey.com',
			type: 'lead',
			guardianType: 'parent'
		})
	})

	test('get', async ()=>{
		const id = 'cool-guy'

		mockAxios.get.mockResolvedValue({
			data: {
				id,
				firstName: 'steve',
				lastName: 'o',
				email: 'steveo@jackdonkey.com',
				type: 'lead',
				guardianType: 'parent',
				children: []
			}
		})

		const customer = await api.get()
		expect(mockAxios.get).toHaveBeenCalledWith('v1/customers/current_user/')
		expect(customer).toMatchObject({
			id,
			firstName: 'steve',
			lastName: 'o',
			email: 'steveo@jackdonkey.com',
			type: 'lead',
			guardianType: 'parent',
			children: []
		})
	})

	test('update', async ()=>{
		const id = 'cool-guy'
		const payload = {
			id,
			firstName: 'Steven'
		}
		mockAxios.patch.mockResolvedValue({
			data: {
				id,
				firstName: 'Steven',
				lastName: 'o',
				email: 'steveo@jackdonkey.com',
				type: 'lead',
				guardianType: 'parent',
				children: []
			}
		})

		const customer = await api.update(payload)
		expect(mockAxios.patch).toHaveBeenCalledWith('/v1/customers/cool-guy/',{
			firstName: 'Steven'
		})
		expect(customer).toMatchObject({
			id,
			firstName: 'Steven',
			lastName: 'o',
			email: 'steveo@jackdonkey.com',
			type: 'lead',
			guardianType: 'parent',
			children: []
		})
	})

	test('create customer password ', async ()=>{
		mockAxios.post.mockResolvedValueOnce({
			data: {
				message: 'password set, goodbye'
			}
		})
		await api.createCustomerPassword({
			id: 'dank-customer-id',
			password: 'you\'ll-never-guess-this'
		})

		expect(mockAxios.post).toHaveBeenCalledWith(
			'/v1/customers/dank-customer-id/set_password/',
			{password: 'you\'ll-never-guess-this'}
		)
	})
})
