import { isRejectedWithValue } from '@reduxjs/toolkit'

import { CartType } from 'api/CartAPI/types'
import { CartSliceState, updateCartLineItems } from 'store/cartSlice'
import { dispatch } from 'store/store'
import { createSubscription, SubscriptionSliceState, updateSubcriptionChargeDate } from 'store/subscriptionSlice'
import { CreateCustomerSubscriptionPayload } from 'api/SubscriptionAPI/types'
import { defaultTo, isEmpty } from 'lodash'
import { OrderType } from 'api/OrderAPI/types'
import moment, { Moment } from 'moment'
import { RenderSuccessToast } from 'components/Toast'
import analyticsClient from 'src/libs/analytics'


class RenderChildOrderInfoViewControllerMethods{
	
	private subscription:SubscriptionSliceState
	private orders: Record<string, OrderType>
	private carts: CartSliceState

	constructor(
		subscription:SubscriptionSliceState, 
		orders: Record<string, OrderType>,
		carts: CartSliceState
	){
		this.subscription = subscription
		this.orders = orders
		this.carts = carts
	}
	
	onSubmitMealPlan = (hideMealPlan:()=> void) => async (cart: CartType)=>{
		await analyticsClient.updateSubscription({
			first_name: this.subscription.firstName,
			last_name: this.subscription.lastName,
			email: this.subscription.email,
			lineItems: cart.lineItems.map(({product,quantity})=>{
				return {
					title: product?.title,
					quantity,
				}
			})
		})
		return dispatch(updateCartLineItems({
			cartId: cart.cartId,
			customerId: this.subscription.id,
			lineItems: cart.lineItems
		}))
			.then((action)=>{
				if(!isRejectedWithValue(action)){
					hideMealPlan()
					RenderSuccessToast('Subscription succesfully updated')
				}
			})
	}

	updateBundleInfo = async (payload: CreateCustomerSubscriptionPayload) =>{
		await analyticsClient.updateBundleInfo({
			first_name: this.subscription.firstName,
			last_name: this.subscription.lastName,
			email: this.subscription.email
		})
		await analyticsClient.updateSubscription({
			first_name: this.subscription.firstName,
			last_name: this.subscription.lastName,
			email: this.subscription.email,
			number_of_servings: this.subscription
		})
		return await dispatch(createSubscription(payload))
	}

	getOrder = (id:string)=>{
		return this.orders[id] || {}
	}

	getOrderLineItems = (id:string)=>{
		if(isEmpty(this.orders)) return []
		return this.orders[id] ? defaultTo(this.orders[id].orderLineItems, []) : []
	}

	getDefaultChargeDate = (childId:string)=>{
		const defaultChargeDate = moment().add(1, 'days')
		const childSubscription = this.subscription.subscriptions[childId]
		if(!childSubscription || !childSubscription.nextOrderChargeDate){
			return defaultChargeDate
		}
		return moment(childSubscription.nextOrderChargeDate)
	}

	disabledDate = (date: Moment)=>{
		return date.isBefore(moment()) ||
		date.isAfter(moment().add(2, 'month').add(1, 'days'))
	}

	updateChargeDate = (subscription: string, setShouldShowDatePicker:(showDatePicker: boolean) => void) => 
		async ({chargeDate}: {chargeDate: Moment}) =>{
			const action = await dispatch(
				updateSubcriptionChargeDate({
					subscription,
					nextOrderChargeDate: chargeDate.format('YYYY-MM-DD')
				})
			)
			if(isRejectedWithValue(action)){
				return
			}
			RenderSuccessToast('Charge date succesfully updated')
			setShouldShowDatePicker(false)
		}
}

export type RenderChildOrderInfoViewControllerMembers = {
	fields: {
		subscription: SubscriptionSliceState,
		carts: CartSliceState

	}
	actions: RenderChildOrderInfoViewControllerMethods
}
const RenderChildOrderInfoViewController = (
	subscription:SubscriptionSliceState, 
	orders: Record<string, OrderType>,
	carts: CartSliceState
):RenderChildOrderInfoViewControllerMembers=>{

	const actions = new RenderChildOrderInfoViewControllerMethods(subscription, orders, carts)

	return ({
		fields: {
			subscription,
			carts,
		},
		actions
	})
}

export default RenderChildOrderInfoViewController
