import { renderHook, act } from '@testing-library/react-hooks'

import useOrderMethods from '.'
import mockAxios from 'src/__mocks__/axios'
import { APIstatus } from 'store/types'

describe('useOrderMethods', () => {
	/* 
	this is only being initalized here so
	typecsript can add typing
	*/
	let hook = renderHook(()=> useOrderMethods())

	beforeEach(()=>{
		hook = renderHook(()=> useOrderMethods())
		jest.resetAllMocks()
	})
	test('createOrder: set success status', async () => {
		mockAxios.post.mockResolvedValueOnce({
			data: [
				{
					id: 'some-order-id',
					paymentStatus: 'paid',
					fulfillmentStatus: 'pending',
				}
			]
		})

		await act(async ()=>{
			await hook.result.current.createOrder({
				customer: 'id',
				carts: ['cartID',]
			})
		})

		expect(hook.result.current.error).toEqual('')
		expect(hook.result.current.apiStatus).toEqual(APIstatus.success)
	})

	test('createOrder: set error state', async () => {
		mockAxios.post.mockRejectedValueOnce({
			message: 'error creating error'
		})

		await act(async()=>{
			await hook.result.current.createOrder({
				customer: 'id',
				carts: ['cartID',]
			})
		})

		expect(hook.result.current.error).toBe('There was an error creating your order. Please refresh the page')
		expect(hook.result.current.apiStatus).toBe(APIstatus.error)
	})

	test('fetch shippingRates fetches shipping rates', async () => {
		mockAxios.get.mockResolvedValueOnce({
			data: [
				{id: 'shippingrateID', title: 'flat rate', price: 5.99 }
			]
		})

		await act(async()=>{
			await hook.result.current.fetchShippingRates()
		})
		
		expect(hook.result.current.error).toBe('')
		expect(hook.result.current.apiStatus).toBe(APIstatus.success)
	})

	test('fetch shippingRates fetches shipping rates - error state', async () => {
		mockAxios.get.mockRejectedValueOnce({
			message: 'error fetching shipping rates'
		})

		await act(async()=>{
			await hook.result.current.fetchShippingRates()
		})
		expect(hook.result.current.error).toBe('There was an error fetching shipping rates. Please refresh the page')
		expect(hook.result.current.apiStatus).toBe(APIstatus.error)
	})

	test('fetch discounts fetches active discounts', async () => {
		mockAxios.get.mockResolvedValueOnce({
			data: [
				{id: 'discount', codename: 'FAMILYTHYME', isActive: true, isPrimary: true, bannerText: 'TAKE THYME' }
			]
		})

		await act(async()=>{
			await hook.result.current.fetchDiscounts()
		})

		expect(hook.result.current.error).toBe('')
		expect(hook.result.current.apiStatus).toBe(APIstatus.success)
	})

	test('fetch shippingRates fetches active discounts - error state', async () => {
		mockAxios.get.mockRejectedValueOnce({
			message: 'error fetching shipping rates'
		})

		await act(async()=>{
			await hook.result.current.fetchDiscounts()
		})
		
		expect(hook.result.current.error).toBe('There was an error fetching discounts')
		expect(hook.result.current.apiStatus).toBe(APIstatus.error)
	})

	test('getLatestOrders: fetches latest orders', async ()=>{
		mockAxios.get.mockResolvedValueOnce({
			data: [
				{
					id: 'id1',
					customerChild: 'child',
					paymentStatus: 'paid',
					fullfilmentStatus: 'pending',
					shippingRate: 1.00,
					orderLineItems: []
				}
			]
		})

		await act(async()=>{
			await hook.result.current.getLatestOrders('customer', ['child'])
		})

		expect(hook.result.current.error).toBe('')
		expect(hook.result.current.apiStatus).toBe(APIstatus.success)
	})

	test('getLatestOrders: failing to get latest orders shows error status', async ()=>{
		mockAxios.get.mockRejectedValueOnce({
			message: 'error fetching latest orders'
		})

		await act(async()=>{
			await hook.result.current.getLatestOrders('customer', ['child'])
		})
		
		expect(hook.result.current.error).toBe('There was an error loading your orders. Please refresh the page')
		expect(hook.result.current.apiStatus).toBe(APIstatus.error)
	})
})
