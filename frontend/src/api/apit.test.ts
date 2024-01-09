import axios, { AxiosResponse } from 'axios'
import API from './'

//fake class to test

class FakeClass extends API{
	_createDTO(data: any){
		return this.createDTO(data)
	}

	getClient(){
		return this.client
	}

	getData(data:AxiosResponse){
		return this._data(data)
	}

	_get(url:string){
		return this.client.get(url)
	}

	get queryArgs(){
		return this._queryArgs
	}
}

const fakeClass = new FakeClass({})


describe('API Class', ()=>{

	beforeEach(()=>{
		jest.resetAllMocks()
	})

	test('default config', ()=>{

		new FakeClass({})

		expect(axios.create).toHaveBeenLastCalledWith({
			returnRejectedPromiseOnError: true,
			withCredentials: true,
			timeout: 30000,
			xsrfCookieName: 'csrftoken',
			xsrfHeaderName: 'X-XSRF-TOKEN',
			headers: {
				'Content-Type': 'application/json',
				Accept: 'application/json',
			}
		})

	})

	test('custom config', ()=>{

		new FakeClass({
			timeout: 1,
			withCredentials: false
		})
		
		expect(axios.create).toHaveBeenLastCalledWith({
			returnRejectedPromiseOnError: true,
			withCredentials: false,
			timeout: 1,
			xsrfCookieName: 'csrftoken',
			xsrfHeaderName: 'X-XSRF-TOKEN',
			headers: {
				'Content-Type': 'application/json',
				Accept: 'application/json',
			}
		})

	})

	test('can access client api', async ()=>{
		await fakeClass._get('dankmemes.gov/memes')
		const client = fakeClass.getClient()
		expect(client.get).toHaveBeenCalledWith('dankmemes.gov/memes')
	})

	test('createDTO', ()=>{
		const object = {
			firstName: 'first',
			birthDate: 'birth',
			somethingElse: '...'
		}

		const newObject = fakeClass._createDTO(object)

		expect(newObject).toMatchObject({
			firstName: 'first',
			birthDate: 'birth',
			somethingElse: '...'
		})
	})

	test('_data', ()=>{
		const data = {
			firstName: 'first',
			birthDate: 'birth',
			somethingElse: '...'
		}

		const response = {
			data
		} as AxiosResponse

		const newObject = fakeClass.getData(response)

		expect(newObject).toMatchObject({
			firstName: 'first',
			birthDate: 'birth',
			somethingElse: '...'
		})
	})

	test('_queryArgs: returns empty string when called without args', ()=>{
		expect(fakeClass.queryArgs()).toBe('')
	})
	test('_queryArgs: returns empty string when called with empty object', ()=>{
		expect(fakeClass.queryArgs({})).toBe('')
	})
	test('_queryArgs: returns query args when called with arg object', ()=>{
		expect(fakeClass.queryArgs({
			is_active: 'true',
			product_type: 'add-on'
		})).toBe('?is_active=true&product_type=add-on')
	})
})
