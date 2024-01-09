import cartReducer, {
	initialState as initCartState,
	getChildrenCarts,
	updateCartLineItems,
	initStore as initCartStore
} from './cartSlice'
import CartAPI from 'src/api/CartAPI'
import store, {AppDispatch} from 'src/store/store'
import {cloneDeep} from 'lodash'

import {APIstatus} from 'store/types'

jest.mock('src/api/CartAPI')
const mockCartAPI = CartAPI as jest.Mocked<typeof CartAPI>

describe('Cart Reducer',  () => {
	beforeEach(() => {
		jest.clearAllMocks()
		cartReducer(undefined, {type: 'reset carts store'})
	})

	const dispatch: AppDispatch = store.dispatch
	const customerId = 'some-customer-id'
	const cartId = 'some-cart-id'
	const childId = 'some-child-id'

	const updateChildCartLineItemsPayload = {
		customerId: customerId,
		cartId: cartId,
		lineItems: [],
	}
	const updateChildCartLineItemsResponse = {
		id: cartId,
		customer: customerId,
		child: childId,
		lineItems: []
	}

	const getChildrenCartsResponse = [{
		child: childId,
		customer: customerId,
		lineItems: updateChildCartLineItemsResponse.lineItems,
	}]

	describe('init store', () => {
		test('should return initial state', () => {
			const initCartStoreCopy = cloneDeep(initCartState)
			mockCartAPI.getChildrenCarts.mockResolvedValueOnce(getChildrenCartsResponse as any)
			const state = cartReducer(undefined, {type: 'fake action'})

			expect(state).toMatchObject(initCartStoreCopy)
		})
	})
	describe('getChildrenCarts CRUD', () => {
		describe('carts.getChildrenCarts', () => {
			const errorMessage = 'Server Error'
			const expectedState = {
				...(initCartStore),
				APIStatus: APIstatus.error,
				error: errorMessage,
				init: false
			}
			test('returns api status of loading when still fetching data', async () => {
				const action = getChildrenCarts.pending('', 'some-customer-id', {})
				const result = cartReducer(initCartState, action)
				expect(result.APIStatus).toBe(APIstatus.loading)
			})
			test('returns data on successful api response', async () => {
				mockCartAPI.getChildrenCarts.mockResolvedValueOnce(getChildrenCartsResponse as any)
				await dispatch(getChildrenCarts(customerId))
				expect(mockCartAPI.getChildrenCarts).toHaveBeenCalledWith(customerId)
			})
			test('returns error message when unsuccessful api response', async () => {
				mockCartAPI.getChildrenCarts.mockRejectedValue(new Error('Server Error'))
				const action = getChildrenCarts.rejected(new Error(errorMessage), '', updateChildCartLineItemsPayload as any, {})
				const result = cartReducer(initCartState, action)
				expect(result.error).toBe(expectedState.error)
			})
		})
		describe('carts.updateCartLineItems', () => {
			test('returns error message when unsuccessful api response happens', async () => {
				const errorMessage = 'Server Error'
				const expectedState = {
					...(initCartStore),
					APIStatus: APIstatus.error,
					error: errorMessage,
					init: false
				}
				mockCartAPI.updateCartLineItems.mockRejectedValue(new Error('Server Error'))
				const action = updateCartLineItems.rejected(new Error(errorMessage), '', updateChildCartLineItemsPayload, {})
				const result = cartReducer(initCartState, action)
				expect(result.error).toBe(expectedState.error)
			})
			test('should return with updated cart', async () => {
				const expectedState = {
					...cloneDeep(initCartState),
					children: {
						'some-child-id': {
							cartId: 'some-cart-id',
							id: 'some-child-id',
							lineItems: updateChildCartLineItemsResponse.lineItems,
						}
					},
					APIStatus: APIstatus.success,
				}
				mockCartAPI.updateCartLineItems.mockResolvedValue(updateChildCartLineItemsResponse as any)
				const action = updateCartLineItems.fulfilled(
					updateChildCartLineItemsResponse as any,
					'',
					updateChildCartLineItemsPayload as any,
					{}
				)
				const state = cartReducer(initCartState, action)
				expect(state).toMatchObject(expectedState)
			})
		})
	})
})
