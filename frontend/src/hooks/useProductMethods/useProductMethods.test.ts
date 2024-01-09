import { renderHook, act } from '@testing-library/react-hooks'

import useProductMethods from '.'
import mockAxios from 'src/__mocks__/axios'

describe('useProductMethods', ()=>{
	/* this is only being initalized here so
	typecsript can add typing
	*/
	let hook = renderHook(()=> useProductMethods())

	beforeEach(()=>{
		hook = renderHook(()=> useProductMethods())
		jest.resetAllMocks()
	})

	describe('init', ()=>{
		test('instance returns default state', ()=>{
			const {
				init,
				APIStatus,
				error
			} = hook.result.current

			const state = {
				init,
				APIStatus,
				error
			}

			expect(state).toEqual({
				init: false,
				APIStatus: 'idle',
				error: ''
			})
		})
	})

	describe('useProductMethods', ()=>{
		test('shows proper success state', async()=>{
			mockAxios.get.mockResolvedValueOnce({data:[
				{
					id: 'string',
					title: 'product',
					iamgeUrl: 'img.png',
					price: 100,
					ingredients: [],
					tags: [],
					ProductType: 'recipe'
				}
			]})

			const expectedState = {
				init: true,
				APIStatus: 'success',
				error: ''
			}

			let products
			
			await act( async ()=>{
				products = await hook.result.current.getProducts()
			})

			const {
				init,
				APIStatus,
				error
			} = hook.result.current

			expect({
				init,
				APIStatus,
				error
			}).toEqual(expectedState)

			expect(products).toEqual([
				{
					id: 'string',
					title: 'product',
					iamgeUrl: 'img.png',
					price: 100,
					ingredients: [],
					tags: [],
					ProductType: 'recipe'
				}
			])
		})

		test('shows error state when api call fails', async ()=>{
			mockAxios.get.mockRejectedValueOnce('sorry, something went wrong')

			await act( async ()=>{
				await hook.result.current.getProducts()
			})

			const {
				init,
				APIStatus,
				error
			} = hook.result.current

			expect({
				init,
				APIStatus,
				error
			}).toEqual({
				init: false,
				APIStatus: 'error',
				error: 'There was an error loading products, please try reloading the page'
			})
			
		})
	})
	
})
