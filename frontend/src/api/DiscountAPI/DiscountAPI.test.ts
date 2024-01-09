import mockAxios from 'src/__mocks__/axios'

import {DiscountAPI} from './'

class API extends DiscountAPI{
	getClient(){
		return this.client
	}
}

describe('DiscountAPI', ()=>{
	const api = new API({})
	beforeEach(()=>{
		jest.resetAllMocks()
	})
	
	describe('getPrimaryDiscount', ()=>{
		test('Gets called with proper arguments', async ()=>{
			mockAxios.get.mockResolvedValueOnce({
				data: [
					{
						id: 'id',
						codename: 'TINYTHYME',
						isActive: true,
						isPrimary: true,
						bannerText: 'Get a nice discount with TINYTHYME'
					}
				]
			})
	
			await api.getPrimaryDiscount()
	
			expect(api.getClient().get).toHaveBeenCalledWith(
				'/v1/discounts/?primary=true',
			)
		})
	})
})
