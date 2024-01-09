import {useState} from 'react'

import { OrderType } from 'api/OrderAPI/types'
import useOrderMethods, { UserOrderMethods } from 'src/hooks/useOrderMethods'
import useBillingMethods, { UseBillingMethods } from 'src/hooks/useBillingMethods'
import { RouterProps, useHistory } from 'react-router-dom'
import { dispatch } from 'store/store'
import { cancelSubscription } from 'store/subscriptionSlice'
import { APIstatus } from 'store/types'
import { isRejectedWithValue } from '@reduxjs/toolkit'

type ViewControllerContructorFields = {
	postCancellationAPIStatus: APIstatus
	cancellationRedemption?: boolean
	subscriptionCancellation?: boolean
	setShouldShowPostCancellationModal: (show: boolean) => void
}

type ViewControllerConstructorSetters = {
	history: RouterProps['history']
	orderMethods: UserOrderMethods
	billingMethods: UseBillingMethods
	setLoading: (loading: boolean) => void,
	setOrders: (order: Record<string, OrderType>) => void,
	setShouldShowPostCancellationModal: (show: boolean) => void
	setPostCancellationAPIStatus: (status: APIstatus) => void
}

type ViewControllerFields = {
	loading: boolean
	orders: Record<string, OrderType>
	renderErrorPage: boolean
	showPostCancellationModal: boolean
	postCancellationAPIStatus: APIstatus
}

class ViewControllerMethods{
	private fields: ViewControllerContructorFields;
	private setters: ViewControllerConstructorSetters;

	constructor(fields: ViewControllerContructorFields, setters: ViewControllerConstructorSetters){
		this.fields = fields
		this.setters = setters
	}

	init(customer:string, childIds: Array<string>){
		this.setters.orderMethods
			.getLatestOrders(customer, childIds)
			.then((orders)=>{
				if(!orders){
					// alert('failed to load orders')
					// this.setters.setRenderErrorPage(true)
				}
				else{
					this.setters.setOrders(this._parseOrders(orders))
				}
				this.setters.setLoading(false)
			})
	}

	get orderMethods(){
		return this.setters.orderMethods
	}

	get cancellationTransactionType(){
		if(this.fields.cancellationRedemption){
			return 'couponRedemption'
		}
		return 'cancellation'
	}

	redeemCancellationCoupon(customerID: string){
		this.fields.setShouldShowPostCancellationModal(true)
		const params = new URLSearchParams(window.location.search)

		const session = params.get('session') || ''
		const subscriptionID = params.get('subscription') || ''
		const discount = params.get('coupon_code') || ''

		this.setters.billingMethods
			.applyCancellationDiscount({
				customer: customerID,
				session,
				subscription: subscriptionID,
				discount,
			})
			.then((data)=>{
				if(data){
					this.setters.setPostCancellationAPIStatus(APIstatus.success)	
				}
				else{
					this.setters.setPostCancellationAPIStatus(APIstatus.error)
				}
			})
	}

	onCloseCancellationModal = ()=>{
		// we redirect back to the dashboard page to remove cancellation params
		
		this.setters.history.replace('/dashboard')
		this.setters.setShouldShowPostCancellationModal(false)
	}

	cancelUserSubscription(){
		this.setters.setShouldShowPostCancellationModal(true)
		const params = new URLSearchParams(window.location.search)
		const subscriptionID = params.get('subscription') || ''
		dispatch(cancelSubscription(subscriptionID)).then((action)=>{
			if(!isRejectedWithValue(action)){
				this.setters.setPostCancellationAPIStatus(APIstatus.success)
			}
			else{
				this.setters.setPostCancellationAPIStatus(APIstatus.error)
			}
		})
	}

	private _parseOrders(orders: Array<OrderType>){
		const orderMap:Record<string, OrderType> = {}
		orders.forEach((order)=>{
			orderMap[order.customerChild] = order
		})
		return orderMap
	}
}

type ViewControllerMembers = ViewControllerFields & {

	actions: ViewControllerMethods
}

export interface viewControllerArguments{
	cancellationRedemption?: boolean
	subscriptionCancellation?: boolean
}
const viewController = ({
	subscriptionCancellation,
	cancellationRedemption,
}:viewControllerArguments):ViewControllerMembers => {
	const [loading, setLoading] = useState(false)
	const [postCancellationAPIStatus, setPostCancellationAPIStatus] = useState<APIstatus>(APIstatus.loading)
	const [orders, setOrders] = useState<Record<string, OrderType>>({})
	const [renderErrorPage, setRenderErrorPage] = useState(false)
	const orderMethods = useOrderMethods()
	const [showPostCancellationModal,setShouldShowPostCancellationModal] = useState(
		!!(cancellationRedemption || subscriptionCancellation)
	)
	const billingMethods = useBillingMethods()
	const history = useHistory()

	const fields: ViewControllerContructorFields = {
		postCancellationAPIStatus,
		cancellationRedemption,
		subscriptionCancellation,
		setShouldShowPostCancellationModal,
	}

	const setters:ViewControllerConstructorSetters = {
		history,
		setOrders,
		setLoading,
		orderMethods,
		billingMethods,
		setShouldShowPostCancellationModal,
		setPostCancellationAPIStatus
	}

	const vc = new ViewControllerMethods(fields, setters)
	
	return {
		showPostCancellationModal,
		postCancellationAPIStatus,
		loading,
		orders,
		renderErrorPage,
		actions: vc
	}
}

export default viewController
