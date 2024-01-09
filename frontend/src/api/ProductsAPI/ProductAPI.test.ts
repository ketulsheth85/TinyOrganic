import {ProductAPI} from './'
import mockAxios from 'src/__mocks__/axios'


class fakeClass extends ProductAPI{

	getClient(){
		return this.client
	}
}

const api = new fakeClass({})


describe('Product API', ()=>{
	describe('getProducts', ()=>{
		test('Calls right endpoint without query args', async ()=>{
			mockAxios.get.mockResolvedValueOnce([{
				title: 'food',
			}])
			await api.getProducts()
			expect(api.getClient().get).toHaveBeenCalledWith('/v1/products/')
	
		})
		test('Calls right endpoint without query args', async ()=>{
			mockAxios.get.mockResolvedValueOnce([{
				title: 'food',
			}])
			await api.getProducts({
				type: 'add-on',
				is_active: 'true'
			})
			expect(api.getClient().get).toHaveBeenCalledWith('/v1/products/?type=add-on&is_active=true')
	
		})
	})
	describe('getProductsForChild',()=>{
		test('Calls right endpoint without query args', async ()=>{
			mockAxios.get.mockResolvedValueOnce({
				data: {}
			})
			await api.getProductsForChild('childid')
			expect(api.getClient().get).toHaveBeenCalledWith('/v1/customers-children/childid/recommended_products/')
	
		})
	})	
})
