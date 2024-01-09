import {
	Ingredient
} from '../types'
import { startsWith } from 'lodash'

class IngredientAPI {

	ingredients = ['coconut', 'honey', 'milk', 'tomato', 'herbs', 'spices', 'pepper', 'leather']
		.map((name,id)=>({
			name,
			id: id.toString()
		}))

	async getIngredients(
		name: string
	): Promise<Array<Ingredient>>{
		return new Promise((resolve)=>{
			resolve(
				this.ingredients.filter((ingredient)=> startsWith(ingredient.name, name))
			)
		})
	}
}

// Ingredient API singleton
export default new IngredientAPI()
