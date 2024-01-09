import API from '..'
import {
	Ingredient
} from './types'

const BACKEND_URL = '/api'
export class IngredientAPI extends API{

	async getIngredients(
		name: string
	): Promise<Array<Ingredient>>{
		return await this.client
			.get(`/v1/ingredients/?name=${name}`)
			.then((resp)=>{
				return resp.data as Array<Ingredient>
			})
	}
}

// Ingredient API singleton
export default new IngredientAPI({
	baseURL: BACKEND_URL 
})
