import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'

import { APIstatus,
	BaseReducerStateAPI,
} from './types'
import IngredientAPI from 'api/IngredientAPI'
import { Ingredient } from 'api/IngredientAPI/types'


// AlexC todo: update to fetch default recipe values
export const initStore = createAsyncThunk(
	'ingredients/init',
	async (name:string,{rejectWithValue})=>{
		try{
			return await IngredientAPI.getIngredients(name)
		}
		catch(err){
			rejectWithValue('Error getting recipe information')
		}
	}
)


export const getIngredients = createAsyncThunk(
	'ingredients/getIngredients',
	async (name:string,{rejectWithValue})=>{
		try{
			return await IngredientAPI.getIngredients(name) as Array<Ingredient>
		}
		catch(err){
			return rejectWithValue('Error getting recipe information')
		}
	}
)

export interface IngredientSliceState extends BaseReducerStateAPI{
	ingredients: Array<string>
	ingredientsMap: Record<string, Ingredient>
}

export const initialState:IngredientSliceState = {
	init: false,
	APIStatus: APIstatus.idle,
	error: '',
	ingredients: [],
	ingredientsMap: {},
}

export const ingredientSlice = createSlice({
	name: 'ingredient',
	initialState,
	reducers: {
	},
	extraReducers: (builders) =>{
		builders.addCase(initStore.rejected, (state, action)=>{
			state.init = false
			state.APIStatus = APIstatus.error
			state.error = action.error.message
		})
		builders.addCase(initStore.pending, (state)=>{
			state.APIStatus = APIstatus.loading
		})
		builders.addCase(initStore.fulfilled, (state, action)=>{
			state.init = true
			state.APIStatus = APIstatus.success
			if(!action.payload){
				return
			}
			const ingredients:Set<string> = new Set([])

			action.payload.forEach(({name,id})=>{
				ingredients.add(name)
				state.ingredientsMap[name] = {name: name, id}
			})

			state.ingredients = Array.from(ingredients).sort((a,b)=>{
				return a.localeCompare(b)
			})	
			
		})

		builders.addCase(getIngredients.pending, (state)=>{
			state.APIStatus = APIstatus.loading
		})
		builders.addCase(getIngredients.rejected, (state, action)=>{
			state.APIStatus = APIstatus.error
			state.error = action.error.message
		})
		builders.addCase(getIngredients.fulfilled, (state, action)=>{
			const payloadIngredients = action.payload as Ingredient[]
			
			state.init = true
			state.APIStatus = APIstatus.success
			if(!action.payload){
				return
			}
			const ingredients:Set<string> = new Set(state.ingredients)

			payloadIngredients.forEach(({name,id})=>{
				ingredients.add(name)
				state.ingredientsMap[name] = {name: name, id}
			})

			state.ingredients = Array.from(ingredients).sort((a,b)=>{
				return a.localeCompare(b)
			})
		})
	}
})

export default ingredientSlice.reducer
