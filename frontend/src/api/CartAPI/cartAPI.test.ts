import mockAxios from 'src/__mocks__/axios'

import {CartAPI} from './'

class API extends CartAPI {
	getClient() {
		return this.client
	}
}

const api = new API({})

const emptyCartMockData = [
	{
		id: 'some-cart-id',
		customer: '',
		child: '',
		lineItems: [],
	},
]

const mockUpdateCartAPIPayload = [
	{
		quantity: 2,
		product: 'some-product-id'
	}
]



describe('CartAPI', () => {
	test('getChildrenCarts', async () => {
		mockAxios.get.mockResolvedValue({
			data: emptyCartMockData
		})
		await api.getChildrenCarts('some-customer-id')
		expect(api.getClient().get).toHaveBeenCalledWith('/v1/carts/?customer=some-customer-id')
	})

	test('response from getChildrenCarts', async () => {
		mockAxios.get.mockResolvedValue({
			data: emptyCartMockData
		})
		await api.getChildrenCarts('some-customer-id')
		expect(api.getClient().get).toReturnTimes(1)
	})

	test('update cart line item request', async () => {
		mockAxios.patch.mockResolvedValue({
			data: mockUpdateCartAPIPayload
		})
		await api.updateCartLineItems({
			cartId: 'cart-id',
			customerId: 'some-customer-id',
			lineItems: mockUpdateCartAPIPayload as any
		})

		expect(api.getClient().patch)
			.toHaveBeenCalledWith('/v1/carts/cart-id/?customer=some-customer-id', {lineItems: mockUpdateCartAPIPayload})
	})

})
