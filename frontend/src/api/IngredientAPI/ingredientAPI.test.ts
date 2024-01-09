import mockAxios from 'src/__mocks__/axios'

import {IngredientAPI} from './'

class API extends IngredientAPI{
	getClient(){
		return this.client
	}
}

const api = new API({})

describe('Ingredient API', ()=>{
	test('getIngredients', async ()=>{
		mockAxios.get.mockResolvedValue({
			data: {
				name: 'corn',
				id: 'corn-is-good'
			}
		})
		await api.getIngredients('corn')
		expect(api.getClient().get).toHaveBeenCalledWith('/v1/ingredients/?name=corn')
	})
})
