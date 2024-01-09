/**
 * ATTENTION!
 * 
 * do not use the tests here as examples for tests on other files
 * refer to recipeSlice.test for better test examples on testing
 * Redux stores
 */

import {
	cloneDeep
} from 'lodash'

import CustomerAPI from 'src/api/CustomerAPI'
import {
	getCookieValue,
} from 'src/utils/utils'
import store, { AppDispatch } from 'src/store/store'
import subscriptionReducer, {
	initialState as initSubscriptionState,
	createConsumer,
	addHouseHoldInfomation,
	updateChild,
	updateCustomer,
	addCustomerAddress,
	updateCustomerAddress,
	initStore as initSubscriptionStore,
	createSubscription,
	updateSubcriptionChargeDate,
	cancelSubscription,
	reactivateSubscription,
} from './subscriptionSlice'
import { Customer, CustomerStatus, GuardianType } from 'api/CustomerAPI/types'
import { APIstatus, HouseHoldInformationPayload } from './types'
import { ChildrenAllergySeverity, ChildrenType } from 'api/ChildrenAPI/types'
import AddressAPI from 'api/AddressAPI'
import ChildrenAPI from 'api/ChildrenAPI'
import { CreateCustomerSubscriptionPayload, CustomerSubscriptionStatus } from 'api/SubscriptionAPI/types'

// set up mocks
jest.mock('src/api/CustomerAPI')
const mockCustomerAPI = CustomerAPI as jest.Mocked<typeof CustomerAPI>

jest.mock('src/api/AddressAPI')
const mockAddressAPI = AddressAPI as jest.Mocked<typeof AddressAPI>

jest.mock('src/api/ChildrenAPI')
const mockChildrenAPI = ChildrenAPI as jest.Mocked<typeof ChildrenAPI>

jest.mock('src/utils/utils')
const mockGetCookieValue = getCookieValue as jest.MockedFunction<typeof getCookieValue>

describe('Subscription Reducer', ()=>{
	let mockFridge:any = {}

	beforeEach(()=>{
		jest.clearAllMocks()
		subscriptionReducer(undefined, {type: 'reset subscription store'})
		mockFridge = {}
	})

	beforeAll(() => {
		global.Storage.prototype.setItem = jest.fn((key, value) => {
			mockFridge[key] = value
		})
		global.Storage.prototype.getItem = jest.fn((key) => mockFridge[key])
	})

	afterAll(()=>{
		const setItem:any = global.Storage.prototype.setItem
		setItem.mockReset()
		const getItem:any = global.Storage.prototype.getItem
		getItem.mockReset()
	})

	const dispatch:AppDispatch = store.dispatch

	describe('init store ', ()=>{
		test('should return initial state', ()=>{
			const initSubscriptionStoreCopy = cloneDeep(initSubscriptionState)
			const state = subscriptionReducer(undefined, {type: 'fake action'})

			expect(state).toMatchObject(initSubscriptionStoreCopy)
		})

		test('initStore: api gets called without id', async()=>{
			
			mockGetCookieValue.mockReturnValueOnce('')
			await dispatch(initSubscriptionStore())

			expect(mockCustomerAPI.get).toHaveBeenCalled()
		})


		test('initStore.fulfilled: store is succesfully initialized', ()=>{
			const response = {
				firstName: 'Alex',
				lastName: 'Comas',
				email: 'abc@email.com'
			}
			const action = initSubscriptionStore.fulfilled(response, '')
			const expectedState = {
				...initSubscriptionState,
				...response,
				init: true
			}

			const state = subscriptionReducer(initSubscriptionState,action)

			expect(state).toMatchObject(expectedState)
		})

		test('initStore.rejected', ()=>{
			const errorMessage = 'Error finding user'

			const action = initSubscriptionStore.rejected(new Error(errorMessage), '')

			const expectedState = {
				...initSubscriptionState,
				error: errorMessage,
				init: true
			}

			const state = subscriptionReducer(initSubscriptionState,action)

			expect(state).toMatchObject(expectedState)
		})
	})

	describe('createCustomer CRUD', ()=>{

		const createCustomerPayload = {
			firstName: 'bob',
			lastName: 'saget',
			email: 'notfunny@fullhouse.com',
		}

		const customerResponse = {
			...createCustomerPayload,
			id: 'someid',
			status: 'lead',
			guardianType: 'parent',
			hasActiveSubscriptions: false,
			hasPassword: false,
			children: [],
			addresses: []
		} as Customer

		const addHouseholdInfoPayload = {
			children: [
				{
					firstName: 'Rick',
					birthDate: '2020-10-10',
					sex: 'male',
				}
			],
			guardianType: 'caregiver',
			parentID: '12345'
		} as HouseHoldInformationPayload

		describe('customer.createCustomer', ()=>{

			test('returns data on succesful api response ', async ()=>{
				mockCustomerAPI.create.mockResolvedValueOnce({
					id: 'my-new-id',
					firstName: 'name',
					lastName: 'last',
					children: [],
					hasPassword: false,
					email: 'email@email.com',
					guardianType: GuardianType.parent,
					status: CustomerStatus.lead,
					addresses: [],
					hasActiveSubscriptions: false
				})

				await dispatch(createConsumer({
					firstName: 'name',
					lastName: 'last',
					email: 'email@email.com'
				}))

				expect(mockCustomerAPI.create).toHaveBeenCalledWith({
					firstName: 'name',
					lastName: 'last',
					email: 'email@email.com'
				})
			})	

			test('should return updated customer', async ()=>{

				const expectedState = {
					...(initSubscriptionState),
					...cloneDeep(customerResponse),
					APIStatus: APIstatus.success,
					init: true,
				}

				const action = createConsumer.fulfilled(customerResponse, '', createCustomerPayload)
				const result = subscriptionReducer(initSubscriptionState, action)

				expect(result).toMatchObject(expectedState)
			})
	
			test('should return loading state', async ()=>{
			
				const expectedState = {
					...(initSubscriptionState),
					APIStatus: APIstatus.loading,
				}
	
				const action = createConsumer.pending('', createCustomerPayload, createCustomerPayload)
				const result = subscriptionReducer(initSubscriptionState, action)
	
				expect(result).toMatchObject(expectedState)
			})
		
			test('should return error state', async ()=>{
				
				const errorMessage = 'There was an error creating your account, please try again later'
				const expectedState = {
					...(initSubscriptionState),
					APIStatus: APIstatus.error,
					init: false,
					error: errorMessage
				}
	
	
				const action = createConsumer.rejected(new Error(errorMessage), '', createCustomerPayload)
				const result = subscriptionReducer(initSubscriptionState, action)
	
				expect(result).toMatchObject(expectedState)
			})

			test('addHouseHoldInfomation.fulfilled: should return updated customer', async ()=>{

				const children = addHouseholdInfoPayload
					.children.map((child, id)=>{
						return {
							...child,
							firstName: child.firstName || `child-${id}`,
							id: id.toString(),
							parent: '',

						}
					})
				const expectedState = {
					...initSubscriptionState,
					...customerResponse,
					...addHouseholdInfoPayload,
					children,
					APIStatus: APIstatus.success,
					init: true,
				}
				const action = addHouseHoldInfomation.fulfilled({
					...customerResponse,
					...addHouseholdInfoPayload,
					children,
				}, '', addHouseholdInfoPayload)

				const result = subscriptionReducer({
					...(initSubscriptionState),
					init: true
				}, action)
	
				expect(result).toMatchObject(expectedState)
			})
		
			test('addHouseHoldInfomation.rejected: should return error state', async ()=>{
				
				const errorMessage = 'There was an error adding the household information to your account'
				const expectedState = {
					...(initSubscriptionState),
					APIStatus: APIstatus.error,
					init: false,
					error: errorMessage
				}
	
	
				const action = createConsumer.rejected(new Error(errorMessage), '', createCustomerPayload)
				const result = subscriptionReducer(initSubscriptionState, action)
	
				expect(result).toMatchObject(expectedState)
			})

		})

		describe('updateCustomer', ()=>{
			test('updateCustomer successful api call', async ()=>{
				await dispatch(updateCustomer({
					firstName: 'Rick',
					lastName: 'Scott'
				}))
				expect(mockCustomerAPI.update).toHaveBeenCalledWith({
					firstName: 'Rick',
					lastName: 'Scott'
				})
			})

			test('updateCustomer rejected with proper error', async ()=>{
				mockCustomerAPI.update.mockRejectedValue(new Error('Something wen\'t wrong'))
				const action = await dispatch(updateCustomer({
					firstName: 'Rick',
					lastName: 'Scott'
				}))
				expect(mockCustomerAPI.update).toHaveBeenCalledWith({
					firstName: 'Rick',
					lastName: 'Scott'
				})

				expect(action.payload).toBe('Something wen\'t wrong')
			})

			test('updateCustomer.fulfilled: parses data correctly', async ()=>{
	
				const payload = {
					firstName: 'Alex',
					lastName: 'Comas',
					email: 'rickscott@email.com',
					phoneNumber: '7861231234'
				}
	
				const action = updateCustomer.fulfilled(payload,'',{})
				const state = subscriptionReducer(initSubscriptionState, action)
	
				expect(state).toMatchObject({
					...cloneDeep(initSubscriptionState),
					init: true,
					APIStatus: APIstatus.success,
					firstName: 'Alex',
					lastName: 'Comas',
					email: 'rickscott@email.com',
					phoneNumber: '7861231234'
				})
			})
	
			test('updateCustomer.pending: returns loading state', async ()=>{
	
				const action = updateCustomer.pending('somestring',{})
				const state = subscriptionReducer(initSubscriptionState, action)
	
				expect(state).toMatchObject({
					...cloneDeep(initSubscriptionState),
					init: false,
					APIStatus: APIstatus.loading,
				})
			})
	
			test('getIngredients.rejected: returns error state', async ()=>{
	
				const errorMessage = 'Stop asking me for stuff'
	
				const action = updateCustomer.rejected(new Error(errorMessage),'',{})
				const state = subscriptionReducer(initSubscriptionState, action)
	
				expect(state).toMatchObject({
					...cloneDeep(initSubscriptionState),
					init: false,
					APIStatus: APIstatus.error,
					error: 'Stop asking me for stuff'
				})
			})
		})

		describe('addCustomerAddress', ()=>{
			test('addCustomerAddress successful api call', async ()=>{
				await dispatch(addCustomerAddress({
					streetAddress: 'address',
					city: 'city',
					state: 'state',
					customer: 'me',
					zipcode: '12345',
					firstName: '',
					lastName: '',
					email: ''
				}))

				expect(mockAddressAPI.create).toHaveBeenCalledWith({
					streetAddress: 'address',
					city: 'city',
					state: 'state',
					customer: 'me',
					zipcode: '12345',
					firstName: '',
					lastName: '',
					email: ''
				})
			})

			test('addCustomerAddress rejected with proper error', async ()=>{
				mockAddressAPI.create.mockRejectedValueOnce(new Error('Something wen\'t wrong'))
				const action = await dispatch(addCustomerAddress({
					streetAddress: 'address',
					city: 'city',
					state: 'state',
					customer: 'me',
					zipcode: '12345',
					firstName: '',
					lastName: '',
					email: ''
				}))

				expect(mockAddressAPI.create).toHaveBeenCalledWith({
					streetAddress: 'address',
					city: 'city',
					state: 'state',
					customer: 'me',
					zipcode: '12345',
					firstName: '',
					lastName: '',
					email: ''
				})
				expect(action.payload).toBe('Something wen\'t wrong')
			})

			test('addCustomerAddress.fulfilled: parses data correctly', async ()=>{
	
				const payload = {
					customer: 'me',
					streetAddress: 'address',
					city: 'city',
					state: 'state',
					zipcode: '12345',
					firstName: '',
					lastName: '',
					email: ''
				}
	
				const action = addCustomerAddress.fulfilled(payload,'',payload)
				const state = subscriptionReducer(initSubscriptionState, action)
	
				expect(state).toMatchObject({
					...cloneDeep(initSubscriptionState),
					init: true,
					APIStatus: APIstatus.success,
					addresses: [{
						customer: 'me',
						streetAddress: 'address',
						city: 'city',
						state: 'state',
						zipcode: '12345'
					}]
				})
			})
	
			test('addCustomerAddress.pending: returns loading state', async ()=>{
	
				const action = addCustomerAddress.pending('somestring',{
					customer: 'me',
					streetAddress: 'address',
					city: 'city',
					state: 'state',
					zipcode: '12345',
					firstName: '',
					lastName: '',
					email: ''
				})
				const state = subscriptionReducer(initSubscriptionState, action)
	
				expect(state).toMatchObject({
					...cloneDeep(initSubscriptionState),
					init: false,
					APIStatus: APIstatus.loading,
				})
			})
	
			test('addCustomerAddress.rejected: returns error state', async ()=>{
	
				const errorMessage = 'Stop asking me for stuff'
	
				const action = addCustomerAddress.rejected(new Error(errorMessage),'', {
					customer: 'me',
					streetAddress: 'address',
					city: 'city',
					state: 'state',
					zipcode: '12345',
					firstName: '',
					lastName: '',
					email: ''
				})
				const state = subscriptionReducer(initSubscriptionState, action)
	
				expect(state).toMatchObject({
					...cloneDeep(initSubscriptionState),
					init: false,
					APIStatus: APIstatus.error,
					error: 'Stop asking me for stuff'
				})
			})
		})

		describe('updateCustomerAddress', ()=>{
			test('updateCustomerAddress successful api call', async ()=>{
				await dispatch(updateCustomerAddress({
					id: 'myid',
					streetAddress: 'address',
					city: 'city',
					state: 'state',
					customer: 'me',
					zipcode: '12345',
					isActive: false,
					firstName: '',
					lastName: '',
					email: ''
				}))

				expect(mockAddressAPI.update).toHaveBeenCalledWith({
					id: 'myid',
					streetAddress: 'address',
					city: 'city',
					state: 'state',
					customer: 'me',
					zipcode: '12345',
					isActive: false,
					firstName: '',
					lastName: '',
					email: ''
				})
			})

			test('updateCustomerAddress rejected with proper error', async ()=>{
				mockAddressAPI.update.mockRejectedValueOnce(new Error('Something wen\'t wrong'))
				const action = await dispatch(updateCustomerAddress({
					id: 'addressid',
					customer: 'me',
					streetAddress: 'address',
					city: 'city',
					state: 'state',
					zipcode: '12345',
					isActive: false,
					firstName: '',
					lastName: '',
					email: ''
				}))

				expect(mockAddressAPI.update).toHaveBeenCalledWith({
					id: 'addressid',
					customer: 'me',
					streetAddress: 'address',
					city: 'city',
					state: 'state',
					zipcode: '12345',
					isActive: false,
					firstName: '',
					lastName: '',
					email: ''
					
				})
				expect(action.payload).toBe('There was an error updating your address, please try again later')
			})

			test.skip('updateCustomerAddress.fulfilled: parses data correctly', async ()=>{
				// add test here
			})
	
			test('updateCustomerAddress.pending: returns loading state', async ()=>{
	
				const action = updateCustomerAddress.pending('somestring',{
					id: 'address-to-update',
					customer: 'me',
					streetAddress: 'address',
					city: 'city',
					state: 'state',
					zipcode: '12345',
					isActive: true,
					firstName: '',
					lastName: '',
					email: ''
				})
				const state = subscriptionReducer(initSubscriptionState, action)
	
				expect(state).toMatchObject({
					...cloneDeep(initSubscriptionState),
					init: false,
					APIStatus: APIstatus.loading,
				})
			})
	
			test('updateCustomerAddress.rejected: returns error state', async ()=>{
	
				const errorMessage = 'Stop asking me for stuff'
	
				const action = updateCustomerAddress.rejected(new Error(errorMessage),'', {
					id: 'address-to-update',
					customer: 'me',
					streetAddress: 'address',
					city: 'city',
					state: 'state',
					zipcode: '12345',
					isActive: true,
					firstName: '',
					lastName: '',
					email: ''
				})
				const state = subscriptionReducer(initSubscriptionState, action)
	
				expect(state).toMatchObject({
					...cloneDeep(initSubscriptionState),
					init: false,
					APIStatus: APIstatus.error,
					error: 'Stop asking me for stuff'
				})
			})
		})

		describe('children CRUD', ()=>{

			test('returns updated child data on succesful api response ', async ()=>{
				mockChildrenAPI.update.mockResolvedValueOnce({
					id: 'id',
					parent: 'dad',
					firstName: 'me',
					allergies: [],
				})

				await dispatch(updateChild({
					firstName: 'me',
				}))

				expect(mockChildrenAPI.update).toHaveBeenCalledWith({
					firstName: 'me',
				})
			})	

			test('updateChild.fulfilled', ()=>{

				const children:Array<ChildrenType> = [
					{
						parent: 'daddy',
						id: 'tasha',
						firstName: 'Tasha',
						birthDate: '2021/10/10',
						sex: 'female',
						allergySeverity: 'allergic',
						allergies: [
							{id: 'cotton', name: 'cotton',},
						],
					},
					{ 
						parent: 'daddy',
						id: 'id-of-child-to-update',
						firstName: 'Dylan',
						birthDate: '2021/10/10',
						sex: 'male',
						allergySeverity: 'allergic',
						allergies: [
							{id: 'cotton', name: 'cotton',},
							{id: 'taxes', name: 'taxes',}
						],
					},
					{
						parent: 'daddy',
						id: 'tanya',
						firstName: 'Tanya',
						birthDate: '2021/10/10',
						sex: 'male',
						allergySeverity: 'allergic',
						allergies: [
							{id: 'cotton', name: 'cotton',},
							{id: 'taxes', name: 'taxes',}
						],
					},
					{
						parent: 'daddy',
						id: 'rick',
						firstName: 'Rick',
						birthDate: '2021/10/10',
						sex: 'male',
						allergySeverity: 'allergic',
						allergies: [
							{id: 'cotton', name: 'cotton',},
							{id: 'taxes', name: 'taxes',}
						],
					}
				]
				
				const payload = {
					parent: 'daddy',
					id: 'id-of-child-to-update',
					firstName: 'Dylan',
					birthDate: '2021/10/10',
					sex: 'male',
					allergySeverity: 'none' as ChildrenAllergySeverity,
					allergies: []
				}

				const newChildrenArr = cloneDeep(children)

				newChildrenArr[1] = cloneDeep(payload)

				const expectedState = {
					...initSubscriptionState,
					init: true,
					children: newChildrenArr,
				}
				expectedState.APIStatus = APIstatus.success

				
				const action = updateChild.fulfilled(payload, '',payload)
				const state = subscriptionReducer({
					...initSubscriptionState,
					children,
					init: true
				},action)
				expect(state).toMatchObject(expectedState)
			})
		})

		describe('createSubscription', ()=>{
			test('pending: returns loading state', async ()=>{
	
				const action = createSubscription.pending('somestring',{
					customer: 'me',
					customerChild: 'child',
					frequency: 12,
					numberOfServings: 12
				})
				const state = subscriptionReducer(initSubscriptionState, action)
	
				expect(state).toMatchObject({
					...cloneDeep(initSubscriptionState),
					init: false,
					APIStatus: APIstatus.loading,
				})
			})

			test('rejected: returns rejected state', async ()=>{
				const errorMessage = 'Stop asking me for stuff'
	
				const action = createSubscription.rejected(new Error(errorMessage),'', {
					customer: 'me',
					customerChild: 'child',
					frequency: 12,
					numberOfServings: 12
				})
				const state = subscriptionReducer(initSubscriptionState, action)
	
				expect(state).toMatchObject({
					...cloneDeep(initSubscriptionState),
					init: false,
					APIStatus: APIstatus.error,
					error: 'Stop asking me for stuff'
				})
			})

			test('success: returns success state', async ()=>{
				const payload = {
					customer: 'me',
					customerChild: 'child',
					frequency: 12,
					numberOfServings: 12,
					isActive: false
				} as CreateCustomerSubscriptionPayload

				const expectedState = {
					...initSubscriptionState,
					init: true,
					subscriptions: {
						'child': {
							customer: 'me',
							customerChild: 'child',
							frequency: 12,
							numberOfServings: 12,
							isActive: false
						}
					}
				}
				expectedState.APIStatus = APIstatus.success

				
				const action = createSubscription.fulfilled(payload, '',payload)
				const state = subscriptionReducer({
					...initSubscriptionState,
					init: true,
					subscriptions: {
						'child': {
							id: '',
							customer: 'me',
							customerChild: 'child',
							frequency: 12,
							numberOfServings: 12,
							isActive: false,
							status: CustomerSubscriptionStatus.active
						}
					}
				},action)
				expect(state).toMatchObject(expectedState)
			})
		})

		describe('updateSubcriptionChargeDate', ()=>{
			test('pending: returns loading state', async ()=>{
	
				const action = updateSubcriptionChargeDate.pending('somestring',{
					subscription: 'subscriptionId',
					nextOrderChargeDate: '2020-20-10'
				})
				const state = subscriptionReducer(initSubscriptionState, action)
	
				expect(state).toMatchObject({
					...cloneDeep(initSubscriptionState),
					init: false,
					APIStatus: APIstatus.loading,
				})
			})

			test('rejected: returns rejected state', async ()=>{
				const errorMessage = 'Stop asking me for stuff'
	
				const action = updateSubcriptionChargeDate.rejected(new Error(errorMessage),'', {
					subscription: 'subscriptionId',
					nextOrderChargeDate: '2020-20-10'
				})
				const state = subscriptionReducer(initSubscriptionState, action)
	
				expect(state).toMatchObject({
					...cloneDeep(initSubscriptionState),
					init: false,
					APIStatus: APIstatus.error,
					error: 'Stop asking me for stuff'
				})
			})

			test('success: returns success state', async ()=>{
				const payload = {
					subscription: 'subscriptionID',
					nextOrderChargeDate: '2020-20-10'
				}
				const expectedState = {
					...initSubscriptionState,
					init: true,
					subscriptions: {
						'child': {
							customer: 'CustomerID',
							customerChild: 'child',
							frequency: 2,
							numberOfServings: 12,
							isActive: true,
							nextOrderChargeDate: '2020-20-10'
						}
					}
				}
				const response = {
					id: 'subscriptionID',
					customer: 'CustomerID',
					customerChild: 'child',
					numberOfServings: 12,
					frequency: 2,
					isActive: true,
					nextOrderChargeDate: '2020-20-10'
				}
				expectedState.APIStatus = APIstatus.success

				
				const action = updateSubcriptionChargeDate.fulfilled(response, '',payload)
				const state = subscriptionReducer({
					...initSubscriptionState,
					init: true,
					subscriptions: {
						'child': {
							id: 'subscriptionID',
							customer: 'CustomerID',
							customerChild: 'child',
							frequency: 2,
							numberOfServings: 12,
							isActive: true,
							nextOrderChargeDate: '2020-22-10',
							status: CustomerSubscriptionStatus.active
						}
					}
				},action)
				expect(state).toMatchObject(expectedState)
			})
		})

		describe('cancelSubscription', ()=>{
			const cancelSubscriptionResponse = {
				id: 'subscription-id',
				customer: 'customer-id',
				customerChild: 'children-id',
				numberOfServings: 2,
				frequency: 2,
				isActive: false,
				status: 'inactive',
			}
			test('cancelSubscription successful api call', async ()=>{
				const expectedState = {
					...(initSubscriptionState),
					subscriptions: {
						'children-id':{
							id: 'subscription-id',
							customer: 'customer-id',
							customerChild: 'children-id',
							numberOfServings: 2,
							frequency: 2,
							isActive: false,
							status: 'inactive',
						}
					},
					APIStatus: APIstatus.success,
				}

				const action = cancelSubscription.fulfilled(cancelSubscriptionResponse, '', 'subcription-id')
				const result = subscriptionReducer(initSubscriptionState, action)

				expect(result).toMatchObject(expectedState)
			})
			test('cancelSubscription failed api call', async ()=>{
				const expectedState = {
					...(initSubscriptionState),
					error: 'There was an error cancelling your subscription, please try again later',
					APIStatus: APIstatus.error,
				}
				const errorMessage = 'There was an error cancelling your subscription, please try again later'
				const action = cancelSubscription.rejected(new Error(errorMessage), '', 'subcription-id')

				const result = subscriptionReducer(initSubscriptionState, action)

				expect(result).toMatchObject(expectedState)
			})
			test('cancelSubscription pending api call', async ()=>{
				const expectedState = {
					...(initSubscriptionState),
					error: '',
					APIStatus: APIstatus.loading,
				}
				const action = cancelSubscription.pending('', '', 'subcription-id')

				const result = subscriptionReducer(initSubscriptionState, action)

				expect(result).toMatchObject(expectedState)
			})
		})

		describe('reactivateSubscription', ()=>{
			const reactivateSubscriptionResponse = {
				id: 'subscription-id',
				customer: 'customer-id',
				customerChild: 'children-id',
				numberOfServings: 2,
				frequency: 2,
				isActive: true,
				status: 'active',
			}
			test('cancelSubscription successful api call', async ()=>{
				const expectedState = {
					...(initSubscriptionState),
					subscriptions: {
						'children-id':{
							id: 'subscription-id',
							customer: 'customer-id',
							customerChild: 'children-id',
							numberOfServings: 2,
							frequency: 2,
							isActive: true,
							status: 'active',
						}
					},
					APIStatus: APIstatus.success,
				}

				const action = reactivateSubscription.fulfilled(reactivateSubscriptionResponse, '', 'subcription-id')
				const result = subscriptionReducer(initSubscriptionState, action)

				expect(result).toMatchObject(expectedState)
			})
			test('cancelSubscription failed api call', async ()=>{
				const expectedState = {
					...(initSubscriptionState),
					error: 'There was an error activating your subscription, please try again later',
					APIStatus: APIstatus.error,
				}
				const errorMessage = 'There was an error activating your subscription, please try again later'
				const action = reactivateSubscription.rejected(new Error(errorMessage), '', 'subcription-id')

				const result = subscriptionReducer(initSubscriptionState, action)

				expect(result).toMatchObject(expectedState)
			})
			test('cancelSubscription pending api call', async ()=>{
				const expectedState = {
					...(initSubscriptionState),
					error: '',
					APIStatus: APIstatus.loading,
				}
				const action = reactivateSubscription.pending('', '', 'subcription-id')

				const result = subscriptionReducer(initSubscriptionState, action)

				expect(result).toMatchObject(expectedState)
			})
		})
	})
})
