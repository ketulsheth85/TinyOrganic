import {ChildrenAPI} from './'
import mockAxios from 'src/__mocks__/axios'
import { ChildrenType, ChildrenAllergySeverity } from './types'

class fakeClass extends ChildrenAPI{
	_sanitizeChild(child:Partial<ChildrenType>):Partial<ChildrenType>{
		return this.sanitizeChild(child)
	}

	_createDTO(data:Partial<ChildrenType>){
		return this.createDTO(data)
	}
}

const api = new fakeClass({})


describe('receipe api', ()=>{
	test('sanitize child', ()=>{
		const child = {
			sex: '',
			birthDate: '',
			id: 'my-cool-id',
			firstName: 'Tammy'
		}
		
		expect(api._sanitizeChild(child)).toMatchObject({
			firstName: 'Tammy'
		})
	})

	test('createDTO', ()=>{
		const child = {
			sex: 'male',
			birthDate: '',
			id: 'my-cool-id',
			firstName: 'Tammy',
			allergies: [],
			allergySeverity: 'none' as ChildrenAllergySeverity
		}

		expect(api._createDTO(child)).toMatchObject({
			sex: 'male',
			firstName: 'Tammy',
			allergies: [],
			allergySeverity: 'none'
		})
	})

	test('create', async ()=>{
		const child = {
			sex: 'male',
			birthDate: '',
			firstName: 'Tammy',
			allergies: [],
			allergySeverity: 'none' as ChildrenAllergySeverity
		}

		const parent = 'im-your-daddy'

		mockAxios.post.mockResolvedValue({
			id: 'my-cool-id',
			firstName: 'Tammy',
			parent,
			sex: 'male',
			birthDate: '',
			allergies: [],
			allergySeverity: 'none'
		})

		await api.create(child,parent)

		expect(mockAxios.post).toHaveBeenCalledWith(
			'/v1/customers-children/',
			{
				parent: 'im-your-daddy',
				sex: 'male',
				firstName: 'Tammy',
				allergies: [],
				allergySeverity: 'none'
			},
		)
	})

	test('update', async ()=>{
		const parent = 'im-your-daddy'
		const child = {
			parent,
			id: 'my-cool-id',
			sex: 'male',
			birthDate: '',
			firstName: 'Tammy',
			allergies: [],
			allergySeverity: 'none' as ChildrenAllergySeverity
		}

		mockAxios.patch.mockResolvedValue({
			id: 'my-cool-id',
			firstName: 'Tammy',
			parent,
			sex: 'male',
			birthDate: '',
			allergies: [],
			allergySeverity: 'none'
		})

		await api.update(child)

		expect(mockAxios.patch).toHaveBeenCalledWith(
			'/v1/customers-children/my-cool-id/',
			{
				sex: 'male',
				firstName: 'Tammy',
				allergies: [],
				birthDate: '',
				allergySeverity: 'none'
			},
		)
	})

	test('delete', async ()=>{
		const child = 'my-child-id'

		mockAxios.delete.mockResolvedValue({})

		await api.delete(child)

		expect(mockAxios.delete).toHaveBeenCalledWith(
			'/v1/customers-children/my-child-id/')
	})
})
