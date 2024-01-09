import { createSlice, createAsyncThunk, isRejectedWithValue } from '@reduxjs/toolkit'
import { omit, pick, cloneDeep } from 'lodash'

import { APIstatus,
	BaseReducerStateAPI,
	HouseHoldInformationPayload
} from './types'
import CustomerAPI from 'src/api/CustomerAPI'
import ChildrenAPI from 'src/api/ChildrenAPI'
import AddressAPI from 'api/AddressAPI'
import { 
	CustomerCreationPayload,
	Customer,
	CustomerUpdatePayload,
	AddCustomerDetailsPayload,
	GuardianType,
	CustomerStatus
} from 'src/api/CustomerAPI/types'
import { ChildrenCreationPayload, ChildrenID, ChildrenType, ChildrenUpdatePayload } from 'src/api/ChildrenAPI/types'
import { RootState } from './store'
import { CustomerAddress, CustomerAddressCreationPayload, CustomerAddressUpdatePayload } from 'api/AddressAPI/types'
import { CreateCustomerSubscriptionPayload, CustomerSubscription, CustomerSubscriptionCreationResponse, UpdateCustomerSubscriptionChargeDatePayload } from 'api/SubscriptionAPI/types'
import SubscriptionAPI from 'api/SubscriptionAPI'


export const initStore = createAsyncThunk(
	'subscription/init',
	async (_,{rejectWithValue})=>{
		try{
			return await CustomerAPI.get()
		}
		catch(err){
			return rejectWithValue('Error loading account, please try login in or reloading the page')
		}
	}
)

export const initOnboarding = createAsyncThunk(
	'subscription/initOnboarding',
	async (_,{rejectWithValue})=>{
		try{
			return await CustomerAPI.get()
		}
		catch(err){
			return {}
		}
	}
)

export const createConsumer = createAsyncThunk(
	'subscription/createConsumer',
	async (customer:CustomerCreationPayload, {rejectWithValue}) => {
		try{
			return await CustomerAPI.create(customer)
		}
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		catch(err:any){
			return rejectWithValue(
				'There was an error creating your account, please try again later'
			)
		}
	}
)

export const updateCustomer = createAsyncThunk(
	'subscription/updateCustomer',
	async (customer:CustomerUpdatePayload, {rejectWithValue}) => {
		try{
			return await CustomerAPI.update(customer)
		}
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		catch(err:any){
			return rejectWithValue(
				err.message ||
				'There was an error updating your account, please try again later'
			)
		}
	}
)

/**
 * Same as update customer but
 * Sets the customer password,
 * should only be used for onboarding
 */
export const AddCustomerDetails = createAsyncThunk(
	'subscription/createCustomerPassword',
	async (customer:AddCustomerDetailsPayload)=>{
		try{
			await CustomerAPI.createCustomerPassword(
				pick(customer, ['id', 'password'])
			)
			return await CustomerAPI.update(
				omit(customer,['password'])
			)
		}
		catch(err){
			return isRejectedWithValue(
				'There was an error updating your account details, please try again later'
			)
		}
	}
)

export const addCustomerAddress = createAsyncThunk(
	'subscription/addCustomerAddress',
	async (address:CustomerAddressCreationPayload, {rejectWithValue}) => {
		try{		
			return await AddressAPI.create(address)
		}
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		catch(err:any){
			return rejectWithValue(
				err.message ||
					'There was an error adding an address to your account, please try again later'
			)
		}
	}
)

export const updateCustomerAddress = createAsyncThunk(
	'subscription/updateCustomerAddress',
	async (address:CustomerAddressUpdatePayload, {rejectWithValue}) => {
		try{
			return await AddressAPI.update(address)
		}
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		catch(err:any){
			return rejectWithValue(
				'There was an error updating your address, please try again later'
			)
		}
	}
)

export const addHouseHoldInfomation = createAsyncThunk(
	'subscription/addHouseholdInfo',
	async ({
		children,
		guardianType,
		parentID
	}:HouseHoldInformationPayload, {
		rejectWithValue,
		getState
	}) => {

		const {subscription} = getState() as RootState
		const localChildrenIDs = new Set(children
			.map(({id})=> id)
			.filter(Boolean)
		)
		
		try{
			// update parent
			const updatedCustomer = await CustomerAPI.update({
				guardianType,
				id: parentID
			})

			// delete children
			await Promise.all(
				subscription
					.children
					.filter((subscriptionChild)=> 
						(subscriptionChild.id && !localChildrenIDs.has(subscriptionChild.id)))
					.map((child)=> ChildrenAPI.delete(child.id))
			)
			

			// update/create children
			const _children = await Promise.all(
				children.map((child:ChildrenCreationPayload)=>{

					if(child.id){
						return ChildrenAPI.update(child as ChildrenUpdatePayload)
					}
					return ChildrenAPI.create(child, parentID)
				})
			)

			return {
				...updatedCustomer,
				children: _children
			}
		}
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		catch(err:any){
			return rejectWithValue(
				'There was an error updating your household information, please try again later'
			)
		}
	})


export const updateChild = createAsyncThunk(
	'subscription/updateChild',
	async (child:ChildrenUpdatePayload, {rejectWithValue}) => {
		try{
			return await ChildrenAPI.update(child)
		}
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		catch(err:any){
			return rejectWithValue(
				'There was an error creating your account, please try again later'
			)
		}
	})

/**
 * Will create a subcription for a new child customer,
 * if a subscription with the composite child/customer id exists,
 * then that subscription will be updated and returned to the frontend
 */
export const createSubscription = createAsyncThunk(
	'subscription/createSubscription',
	async (payload:CreateCustomerSubscriptionPayload, {rejectWithValue})=>{
		try{
			return await SubscriptionAPI.createSubscription(payload)
		}
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		catch(err:any){
			return rejectWithValue(
				'There was an error adding a meal plan for your child, please try again later'
			)
		}
	})

export const updateSubcriptionChargeDate = createAsyncThunk(
	'subscription/updateSubcriptionChargeDate',
	async (payload:UpdateCustomerSubscriptionChargeDatePayload, {rejectWithValue})=>{
		try{
			return await SubscriptionAPI.updateSubcriptionChargeDate(payload)
		}
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		catch(err:any){
			return rejectWithValue(
				'There was an error updating your charge date, please try again later'
			)
		}
	})

export const preCancelSubscription = createAsyncThunk(
	'subscription/precancelSubscription',
	async (subscription:string, {rejectWithValue})=>{
		try{
			return await SubscriptionAPI.precancelSubscription(subscription)
		}
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		catch(err:any){
			return rejectWithValue(
				'There was an error cancelling your subscription, please try again later'
			)
		}
	}
)

export const cancelSubscription = createAsyncThunk(
	'subscription/cancelSubscription',
	async (subscription:string, {rejectWithValue})=>{
		try{
			return await SubscriptionAPI.cancelSubscription(subscription)
		}
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		catch(err:any){
			return rejectWithValue(
				'There was an error cancelling your subscription, please try again later'
			)
		}
	})

export const reactivateSubscription = createAsyncThunk(
	'subscription/reactivateSubscription',
	async (subscription:string, {rejectWithValue})=>{
		try{
			return await SubscriptionAPI.reactiveSubscription(subscription)
		}
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		catch(err:any){
			return rejectWithValue(
				'There was an error activating your subscription, please try again later'
			)
		}
	})

export interface SubscriptionSliceState extends Customer,BaseReducerStateAPI{
	subscriptions: Record<ChildrenID, CustomerSubscription>
}

export const initialState:SubscriptionSliceState = {
	init: false,
	APIStatus: APIstatus.idle,
	error: '',
	children: [
		{
			firstName: '',
			parent: '',
			id: '',
		},
	],
	firstName: '',
	lastName: '',
	email: '',
	phoneNumber: '',
	hasPassword: false,
	guardianType: GuardianType.parent,
	id: '',
	status: CustomerStatus.lead,
	addresses: [],
	hasActiveSubscriptions: false,
	subscriptions: {}
}

export const subscriptionSlice = createSlice({
	name: 'subscription',
	initialState: cloneDeep(initialState),
	reducers: {
	},
	extraReducers: (builders) =>{

		builders.addCase(initStore.rejected, (state, action)=>{
			state.error = action.error.message
			state.init = true
		})
		builders.addCase(initStore.fulfilled, (state, action)=>{
			const customer = action.payload as Customer
			Object.assign(state,{
				...customer,
				init: true
			})
		})

		builders.addCase(initOnboarding.rejected, (state, action)=>{
			state.error = action.error.message
			state.init = true
		})
		builders.addCase(initOnboarding.fulfilled, (state, action)=>{
			const customer = action.payload as Customer
			Object.assign(state,{
				...customer,
				init: true
			})
		})


		builders.addCase(createConsumer.pending, (state)=>{
			state.APIStatus = APIstatus.loading
		})
		builders.addCase(createConsumer.rejected, (state, action)=>{
			state.APIStatus = APIstatus.error
			state.error = action.error.message
		})
		builders.addCase(createConsumer.fulfilled, (state, action)=>{
			const customer = action.payload as CustomerSubscriptionCreationResponse
			Object.assign(state, {
				...cloneDeep(initialState),
				...customer,
				init: true,
				APIStatus: APIstatus.success
			})
		})

		builders.addCase(updateCustomer.pending, (state)=>{
			state.APIStatus = APIstatus.loading
		})
		builders.addCase(updateCustomer.rejected, (state, action)=>{
			state.APIStatus = APIstatus.error
			state.error = action.error.message
		})
		builders.addCase(updateCustomer.fulfilled, (state, action)=>{
			const customer = action.payload as Customer
			Object.assign(state, {
				...customer,
				init: true,
				APIStatus: APIstatus.success
			})
		})

		builders.addCase(addCustomerAddress.pending, (state)=>{
			state.APIStatus = APIstatus.loading
		})
		builders.addCase(addCustomerAddress.rejected, (state, action)=>{
			state.APIStatus = APIstatus.error
			state.error = action.error.message
		})
		builders.addCase(addCustomerAddress.fulfilled, (state, action)=>{
			const address = action.payload as CustomerAddress
			state.addresses.push(address)
			Object.assign(state, {
				init: true,
				APIStatus: APIstatus.success
			})
		})

		builders.addCase(updateCustomerAddress.pending, (state)=>{
			state.APIStatus = APIstatus.loading
		})
		builders.addCase(updateCustomerAddress.rejected, (state, action)=>{
			state.APIStatus = APIstatus.error
			state.error = action.error.message
		})
		builders.addCase(updateCustomerAddress.fulfilled, (state, action)=>{
			const address = action.payload as CustomerAddress
			for(let i = 0; i < state.addresses.length; i++){
				const curr = state.addresses[i]

				if(curr && curr.id === address.id){
					state.addresses[i] = address
					state.APIStatus = APIstatus.success
					return
				}
			}
			state.addresses.push(address)
			state.APIStatus = APIstatus.success
		})

		builders.addCase(AddCustomerDetails.pending, (state)=>{
			state.APIStatus = APIstatus.loading
		})
		builders.addCase(AddCustomerDetails.rejected, (state, action)=>{
			state.APIStatus = APIstatus.error
			state.error = action.payload as string
		})
		builders.addCase(AddCustomerDetails.fulfilled, (state, action)=>{
			const customer = action.payload as Customer
			Object.assign(state, {
				...customer,
				init: true,
				APIStatus: APIstatus.success
			})
		})

		builders.addCase(addHouseHoldInfomation.pending, (state)=>{
			state.APIStatus = APIstatus.loading
		})
		builders.addCase(addHouseHoldInfomation.rejected, (state, action)=>{
			state.APIStatus = APIstatus.error
			state.error = action.payload as string
		})
		builders.addCase(addHouseHoldInfomation.fulfilled, (state, action)=>{
			const customer = action.payload as Partial<RootState>
			state.APIStatus = APIstatus.success
			Object.assign(state, customer)
		})

		builders.addCase(updateChild.pending, (state)=>{
			state.APIStatus = APIstatus.loading
		})
		builders.addCase(updateChild.rejected, (state, action)=>{
			state.APIStatus = APIstatus.error
			state.error = action.error.message as string
		})
		builders.addCase(updateChild.fulfilled, (state, action)=>{
			const child = action.payload as ChildrenType
			state.APIStatus = APIstatus.success
			for(let i = 0; i < state.children.length; i++){
				if(child.id === state.children[i].id){
					state.children[i] = child
					break
				}
			}
		})

		builders.addCase(createSubscription.pending, (state)=>{
			state.APIStatus = APIstatus.loading
		})
		builders.addCase(createSubscription.rejected, (state, action)=>{
			state.APIStatus = APIstatus.error
			state.error = action.error.message
		})
		builders.addCase(createSubscription.fulfilled, (state, action)=>{
			const subscription = action.payload as CustomerSubscription
			state.APIStatus = APIstatus.success
			state.subscriptions[subscription.customerChild] = subscription
		})

		builders.addCase(updateSubcriptionChargeDate.pending, (state)=>{
			state.APIStatus = APIstatus.loading
		})
		builders.addCase(updateSubcriptionChargeDate.rejected, (state, action)=>{
			state.APIStatus = APIstatus.error
			state.error = action.error.message
		})
		builders.addCase(updateSubcriptionChargeDate.fulfilled, (state, action)=>{
			const subscription = action.payload as CustomerSubscription
			state.APIStatus = APIstatus.success
			state.subscriptions[subscription.customerChild] = subscription
		})

		builders.addCase(preCancelSubscription.pending, (state)=>{
			state.APIStatus = APIstatus.loading
		})
		builders.addCase(preCancelSubscription.rejected, (state, action)=>{
			state.APIStatus = APIstatus.error
			state.error = action.error.message
		})
		builders.addCase(preCancelSubscription.fulfilled, (state)=>{
			// const payload = action.payload as CustomerSubscription
			state.APIStatus = APIstatus.success
			
		})

		builders.addCase(cancelSubscription.pending, (state)=>{
			state.APIStatus = APIstatus.loading
		})
		builders.addCase(cancelSubscription.rejected, (state, action)=>{
			state.APIStatus = APIstatus.error
			state.error = action.error.message
		})
		builders.addCase(cancelSubscription.fulfilled, (state, action)=>{
			const subscription = action.payload as CustomerSubscription
			state.APIStatus = APIstatus.success
			state.subscriptions[subscription.customerChild] = subscription
		})

		builders.addCase(reactivateSubscription.pending, (state)=>{
			state.APIStatus = APIstatus.loading
		})
		builders.addCase(reactivateSubscription.rejected, (state, action)=>{
			state.APIStatus = APIstatus.error
			state.error = action.error.message
		})
		builders.addCase(reactivateSubscription.fulfilled, (state, action)=>{
			const subscription = action.payload as CustomerSubscription
			state.APIStatus = APIstatus.success
			state.subscriptions[subscription.customerChild] = subscription
		})
	}
})

export default subscriptionSlice.reducer
