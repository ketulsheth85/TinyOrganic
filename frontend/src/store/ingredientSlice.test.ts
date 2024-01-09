import { cloneDeep } from 'lodash'

import mockAxios from 'src/__mocks__/axios'
import store from './store'
import ingredientReducer, {
	getIngredients,
	initialState as initialIngredientState,
	initStore
} from './ingredientSlice'
import { deepClone } from 'src/utils/utils'
import { APIstatus } from './types'

describe('Ingredient Reducer',()=>{

	beforeEach(()=>{
		jest.clearAllMocks()
		ingredientReducer(undefined, {type: 'clear-store'})
	})

	const dispatch = store.dispatch

	describe('init store', ()=>{
		test('should return initial state', ()=>{
			const initSubscriptionStoreCopy = cloneDeep(initialIngredientState)
			const state = ingredientReducer(undefined, {type: 'fake action'})

			expect(state).toMatchObject(initSubscriptionStoreCopy)
		})

		test('initStore gets ingredient', async ()=>{
			const response = {
				data: [
					{name: 'korn', id:'id-of-korn'},
				]
			}
			mockAxios.get.mockResolvedValueOnce(response)
			const action = await dispatch(initStore('korn'))
			expect(action.payload).toMatchObject((deepClone(response.data)))
		})

		test('initStore.fulfilled: return proper state on undefined payload', async ()=>{

			const action = initStore.fulfilled(undefined,'','orn')
			const state = ingredientReducer(deepClone(initialIngredientState), action)

			expect(state).toMatchObject({
				...deepClone(initialIngredientState),
				init: true,
				APIStatus: APIstatus.success,
			})
		})

		test('initStore.fulfilled: parses data correctly', async ()=>{

			const payload = [
				{name: 'korn', id:'id-of-korn'},
				{name: 'torn', id:'id-of-torn'},
				{name: 'oorn', id:'id-of-oorn'},
				{name: 'korny', id:'id-of-korny'},
			]

			const action = initStore.fulfilled(payload,'','orn')
			const state = ingredientReducer(initialIngredientState, action)

			expect(state).toMatchObject({
				...deepClone(initialIngredientState),
				init: true,
				APIStatus: APIstatus.success,
				ingredients: ['korn','korny','oorn','torn'],
				ingredientsMap: {
					korn:{name: 'korn', id:'id-of-korn'},
					korny: {name: 'korny', id:'id-of-korny'},
					oorn: {name: 'oorn', id:'id-of-oorn'},
					torn: {name: 'torn', id:'id-of-torn'},
				}
			})
		})

		test('initStore.rejected: returns error state', async ()=>{

			const errorMessage = 'Stop asking me for stuff'

			const action = initStore.rejected(new Error(errorMessage),'','orn')
			const state = ingredientReducer(initialIngredientState, action)

			expect(state).toMatchObject({
				...deepClone(initialIngredientState),
				init: false,
				APIStatus: APIstatus.error,
				error: errorMessage
			})
		})
	})

	describe('getIngredients', ()=>{

		test('initStore gets ingredient', async ()=>{
			const response = {
				data: [
					{name: 'korn', id:'id-of-korn'},
				]
			}
			mockAxios.get.mockResolvedValueOnce(response)
			const action = await dispatch(getIngredients('korn'))
			expect(action.payload).toMatchObject((deepClone(response.data)))
		})

		test('getIngredients.fulfilled: parses data correctly', async ()=>{

			const payload = [
				{name: 'korn', id:'id-of-korn'},
				{name: 'torn', id:'id-of-torn'},
				{name: 'oorn', id:'id-of-oorn'},
				{name: 'korny', id:'id-of-korny'},
			]

			const action = getIngredients.fulfilled(payload,'','orn')
			const state = ingredientReducer(initialIngredientState, action)

			expect(state).toMatchObject({
				...deepClone(initialIngredientState),
				init: true,
				APIStatus: APIstatus.success,
				ingredients: ['korn','korny','oorn','torn'],
				ingredientsMap: {
					korn:{name: 'korn', id:'id-of-korn'},
					korny: {name: 'korny', id:'id-of-korny'},
					oorn: {name: 'oorn', id:'id-of-oorn'},
					torn: {name: 'torn', id:'id-of-torn'},
				}
			})
		})

		test('getIngredients.pending: returns loading state', async ()=>{
			const action = getIngredients.pending('orn','','orn')
			const state = ingredientReducer(initialIngredientState, action)

			expect(state).toMatchObject({
				...deepClone(initialIngredientState),
				init: false,
				APIStatus: APIstatus.loading,
			})
		})

		test('getIngredients.rejected: returns error state', async ()=>{

			const errorMessage = 'Stop asking me for stuff'

			const action = getIngredients.rejected(new Error(errorMessage),'','orn')
			const state = ingredientReducer(initialIngredientState, action)

			expect(state).toMatchObject({
				...deepClone(initialIngredientState),
				init: false,
				APIStatus: APIstatus.error,
				error: errorMessage
			})
		})
	})
})
