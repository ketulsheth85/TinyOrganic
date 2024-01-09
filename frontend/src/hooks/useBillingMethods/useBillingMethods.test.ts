import { renderHook, act } from '@testing-library/react-hooks'

import useBillingMethods from '.'
import mockAxios from 'src/__mocks__/axios'
import { APIstatus } from 'store/types'
import { CustomerSubscriptionStatus } from 'api/SubscriptionAPI/types'


describe('useBillingMethods',()=>{
	/* this is only being initalized here so
	typecsript can add typing
	*/
	let hook = renderHook(()=> useBillingMethods())

	beforeEach(()=>{
		hook = renderHook(()=> useBillingMethods())
		jest.resetAllMocks()
	})

	describe('createPaymentIntent', ()=>{
		test('set success status and return payment intent', async ()=>{
			mockAxios.post.mockResolvedValueOnce({
				data: {
					intentId: 'intent'
				}
			})
	
			let intent

			await act( async ()=>{
				intent = await hook.result.current.createPaymentIntent({
					customer: 'id',
					items: [{id:'id'}]
				})
			})
			
			expect(hook.result.current.apiStatus).toEqual(APIstatus.success)
			expect(hook.result.current.error).toEqual('')
			expect(intent).toEqual({
				intentId: 'intent'
			})
		})
	
		test('set error state and return nothing', async ()=>{
			mockAxios.post.mockRejectedValueOnce({
				message: 'You have failed this city'
			})
	
			await act(async ()=>{
				await hook.result.current.createPaymentIntent({
					customer: 'id',
					items: [{id:'id'}]
				})
			})
	
			// failure status
			expect(hook.result.current.apiStatus).toEqual(APIstatus.error)
			expect(hook.result.current.error).toEqual('There was an error creating your billing profile, please refresh the page')
	
		})
	})

	describe('processPayment ', ()=>{

		beforeEach(()=>{
			jest.resetAllMocks()
		})

		test('returns correct status when payment is processed', async ()=>{
			mockAxios.post.mockResolvedValueOnce({data:{}})
			mockAxios.post.mockResolvedValueOnce({data:{}})

			await act(async ()=>{
				await hook.result.current.processPayment({
					paymentCustomer: 'paymentCustomerID',
					customer: 'customerID',
					paymentMethod: 'paymentMethod',
					amount: 10
				})
			})

			const {apiStatus, error} = hook.result.current
			expect(apiStatus).toBe(APIstatus.success)
			expect(error).toBe('')
		})
	})

	describe('createPaymentMethod', ()=>{
		test('return payment method', async ()=>{
			mockAxios.post.mockResolvedValueOnce({
				data: {
					id: 'id',
					stripeCustomer: 'StripeCustomerID',
					customer: 'CustomerID',
					paymentMethod: 'string',
					lastFour: 1234,
					expirationDate: '2029/01/01'
				}
			})
	
			let customer
			await act(async()=>{
				customer = await hook.result.current.createPaymentMethod({
					customer: 'id',
					paymentMethod: 'string',
					paymentCustomer: 'StripeCustommerID'
				})
			})
	
			// success
			expect(hook.result.current.apiStatus).toEqual(APIstatus.success)
	
			expect(customer).toEqual({
				id: 'id',
				stripeCustomer: 'StripeCustomerID',
				customer: 'CustomerID',
				paymentMethod: 'string',
				lastFour: 1234,
				expirationDate: '2029/01/01'
			})
	
		})
		test('Sends expected error on on failure', async ()=>{
			mockAxios.post.mockRejectedValue('Whoops!')

			await act(async()=>{
				await hook.result.current.createPaymentMethod({
					customer: 'id',
					paymentMethod: 'string',
					paymentCustomer: 'StripeCustommerID'
				})
			})
			const {error, apiStatus} = hook.result.current
			expect(apiStatus).toBe('error')
			expect(error).toBe('There was an error creating your billing profile, please try again later')
		})
	})

	describe('getOrderSummary', ()=>{

		test('Returns subscription with only meal plan info for child without add-ons', async()=>{

			const carts = {
				'childone': {
					cartId: 'cartid1',
					lineItems: [
						{
							id: 'item',
							product: {
								id: 'some-id',
								title: 'some-product',
								productType: 'recipe',
							},
							quantity: 10,
							productVariant: {
								price: 5.49
							}
						},
						{
							id: 'item2',
							product: {
								id: 'some-id2',
								title: 'some-product2',
								productType: 'recipe',
							},
							quantity: 2,
							productVariant: {
								price: 6.49
							}
						}
					],		
				},
			}
	
			const subscriptions = {
				'childone': {
					id: 'string1',
					customer: 'CustomerID',
					customerChild: 'childone',
					numberOfServings: 12,
					frequency: 2,
					isActive: false,
					status: 'active' as CustomerSubscriptionStatus
				},
			}
	
			const children = [
				{
					id:'childone',
					parent: 'CustomerID',
					firstName: 'Rick',
				},
			]

			const expectedPayload =[
				{
					customerID: 'CustomerID',
					cartID: 'cartid1',
					childID: 'childone',
					title: 'Rick\'s Meal Plan',
					description: '12 Meals • Every 2 Weeks',
					isMealPlan: true,
					price: 67.88
				}
			]
			let orderSummaries
			await act(async()=>{
				orderSummaries = await hook.result.current
					.getOrderSummary(children,subscriptions,carts)
			})
			expect(orderSummaries).toEqual(expectedPayload)
		})

		test('Returns subscription with add-on and meal info for cart with add-ons', async()=>{

			const carts = {
				'childone': {
					cartId: 'cartid1',
					lineItems: [
						{
							id: 'item',
							product: {
								id: 'some-id',
								title: 'some-product',
								productType: 'recipe',
							},
							productVariant: {
								price: 5.89
							},
							quantity: 10
						},
						{
							id: 'item2',
							product: {
								id: 'some-id2',
								title: 'some-product2',
								productType: 'recipe',
							},
							productVariant: {
								price: 5.89
							},
							quantity: 2,
						},
						{
							id: 'item3',
							product: {
								id: 'some-id3',
								title: 'Mighty Meals',
								productType: 'add-on',
								price: 15.99
							},
							productVariant: {
								price: 15.99
							},
							quantity: 1,
						}
					],
					
				},
			}
	
			const subscriptions = {
				'childone': {
					id: 'string1',
					customer: 'CustomerID',
					customerChild: 'childone',
					numberOfServings: 12,
					frequency: 2,
					isActive: false,
					status: 'active' as CustomerSubscriptionStatus
				},
			}
	
			const children = [
				{
					id:'childone',
					parent: 'CustomerID',
					firstName: 'Chris',
				},
			]

			const expectedPayload =[
				{
					customerID: 'CustomerID',
					cartID: 'cartid1',
					childID: 'childone',
					title: 'Chris\'s Meal Plan',
					description: '12 Meals • Every 2 Weeks',
					isMealPlan: true,
					price: 70.68
				},
				{
					customerID: 'CustomerID',
					cartID: 'cartid1',
					childID: 'childone',
					title: 'Chris\'s Mighty Meals',
					description: '1x at $15.99',
					productID: 'some-id3',
					isMealPlan: false,
					price: '15.99'
				},
			]
			let orderSummaries
			await act(async()=>{
				orderSummaries = await hook.result.current
					.getOrderSummary(children,subscriptions,carts)
			})
			expect(orderSummaries).toEqual(expectedPayload)
		})
	})

	describe('getLatestPaymentMethod', ()=>{
		test('Has success status on successful api request', async()=>{
			mockAxios.get.mockResolvedValueOnce({
				data: {
					id: 'paymentMethodId',
					customer: 'customer',
					lastFour: 1234,
					expirationDate: '11/10'
				}
			})

			let paymentMethod
			await act(async ()=>{
				paymentMethod = await hook.result.current
					.getLatestPaymentMethod('customer')
			})

			expect(paymentMethod).toEqual({
				id: 'paymentMethodId',
				customer: 'customer',
				lastFour: 1234,
				expirationDate: '11/10'
			})

			expect(hook.result.current.error).toBe('')
			expect(hook.result.current.apiStatus).toBe('success')
		})

		test('Has error status on bad api request', async()=>{
			mockAxios.get.mockRejectedValueOnce({
				detail: 'This is serious'
			})

			await act(async ()=>{
				await hook.result.current
					.getLatestPaymentMethod('customer')
			})

			expect(hook.result.current.error)
				.toBe('There was an error loading your billing info, try again later')
			expect(hook.result.current.apiStatus).toBe('error')
		})
	})
})
