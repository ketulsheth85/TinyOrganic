import { useState } from 'react'

import OrderAPI from 'api/OrderAPI'
import { APIstatus } from 'store/types'
import {OrderCreationPayload, OrderCreationResponse, 
	ShippingRatesResponse, DiscountsResponse, OrderType
} from 'api/OrderAPI/types'
import { CustomerID, CustomerStatus } from 'api/CustomerAPI/types'
import { ChildrenID } from 'api/ChildrenAPI/types'
import CustomerAPI from 'api/CustomerAPI'

export interface UserOrderMethods {
	createOrder: (payload: OrderCreationPayload) => Promise<OrderCreationResponse | void>
	getLatestOrders: (customer: CustomerID, children: Array<ChildrenID>) => Promise<Array<OrderType> | void>
	fetchShippingRates: () => Promise<ShippingRatesResponse | void>
	fetchDiscounts: () => Promise<DiscountsResponse | void>
	error: string
	apiStatus: APIstatus
}

const useOrderMethods = (): UserOrderMethods => {
	const [apiStatus, setApiStatus] = useState(APIstatus.idle)
	const [error, setError] = useState('')
	const setLoadingStatus = ()=>{
		setApiStatus(APIstatus.loading)
		setError('')
	}
	const setErrorStatus = (error:string)=>{
		setApiStatus(APIstatus.error)
		setError(error)
	}
	const setSuccessStatus = ()=>{
		setApiStatus(APIstatus.success)
	}

	const getLatestOrders = async (customer: CustomerID, children: Array<ChildrenID>): Promise<Array<OrderType> | void>=>{
		setLoadingStatus()
		try{
			return await Promise.all(children.map((child)=>{
				return OrderAPI.getLatestOrder(customer, child)
			})).then((data)=>{
				setSuccessStatus()
				return data
			})
		}
		catch(err){
			const error = 'There was an error loading your orders. Please refresh the page'
			setErrorStatus(error)
		}
	}

	const updateUserToSubscriberStatus = (customer:string)=>{
		CustomerAPI.update({
			id: customer,
			status: CustomerStatus.subscriber
		}).catch((err)=>{
			/**
			 * We do nothing here as we want don't want the user
			 * to get charged and still get an error message
			 * 
			 * Note that if this fails, the user will not be able
			 * to login without contacting support to switch their
			 * status to subscriber
			 */
		})
	}

	const createOrder = async (payload: OrderCreationPayload): Promise<OrderCreationResponse | void> => {
		setLoadingStatus()
		return await OrderAPI.createOrder(payload)
			.then(async(data) => {
				await updateUserToSubscriberStatus(payload.customer)
				setSuccessStatus()
				return data
			}).catch(() => {
				const error = 'There was an error creating your order. Please refresh the page'
				setErrorStatus(error)
			})
	}

	const fetchShippingRates = async (): Promise<ShippingRatesResponse | void> => {
		setLoadingStatus()
		return await OrderAPI.fetchShippingRates().then((data) => {
			setSuccessStatus()
			return data
		}).catch(() => {
			const error = 'There was an error fetching shipping rates. Please refresh the page'
			setErrorStatus(error)
		})
	}

	const fetchDiscounts = async (): Promise<DiscountsResponse | void> => {
		setLoadingStatus()
		return await OrderAPI.fetchDiscounts().then((data) => {
			setSuccessStatus()
			return data
		}).catch(() => {
			const error = 'There was an error fetching discounts'
			setErrorStatus(error)
		})
	}

	return ({
		createOrder,
		getLatestOrders,
		fetchShippingRates,
		fetchDiscounts,
		error,
		apiStatus
	})
}

export default useOrderMethods
