import { useState } from 'react'
import { round } from 'lodash'
/**
 * Provides common payment processing methods, but
 * does not keep any billing info to stay PCI compliant
 * 
 * This is used as opposed to a redux store, because their is
 * no data that needs to be used accross the application
 */

import BillingAPI from 'api/BillingAPI'
import { APIstatus } from 'src/store/types'
import { CreateCancellationDiscountPayload, 
	CreateChargePayload, 
	CreatePaymentIntentPayload, 
	CreatePaymentMethodPayload, 
	PaymentIntentResponse, 
	PaymentMethod 
} from 'api/BillingAPI/types'
import { CustomerSubscription } from 'api/SubscriptionAPI/types'
import { ChildrenID, ChildrenType } from 'api/ChildrenAPI/types'
import { CartID } from 'api/OrderAPI/types'
import { CartType } from 'api/CartAPI/types'
import { Product } from 'api/ProductsAPI/types'
import { CustomerID } from 'api/CustomerAPI/types'
import { RenderErrorToast, RenderSuccessToast } from 'components/Toast'

export type ProcessPaymentPayload = CreateChargePayload & CreatePaymentMethodPayload
export type OrderSummary = {
	customerID: string
	productID?: string
	title: string
	description: string
	cartID: CartID
	childID: ChildrenID
	price?: number | string
	isMealPlan: boolean
}

export interface UseBillingMethods{
	createPaymentIntent: (payload:CreatePaymentIntentPayload) => Promise<PaymentIntentResponse | void>
	createPaymentMethod: (payload: CreatePaymentMethodPayload) => Promise<PaymentMethod | void>
	processPayment: (payload: ProcessPaymentPayload) => Promise<void>
	getOrderSummary: (
		children:Array<ChildrenType>,
		subscriptions:Record<string, CustomerSubscription>,
		carts: Record<string, any>
	) =>  Array<OrderSummary>
	error: string
	apiStatus: APIstatus
	getLatestPaymentMethod: (customer: CustomerID) => 
	Promise<Pick<PaymentMethod, 'customer' | 'id' | 'lastFour' | 'expirationDate'> | undefined>
	applyDiscountCode: (customer: CustomerID, discountCode: string) => Promise<any>
	applyCancellationDiscount: (discountPayload: CreateCancellationDiscountPayload) => Promise<any>
}



const useBillingMethods = ():UseBillingMethods=>{

	const [error, setError] = useState('')
	const [apiStatus, setAPIStatus] = useState(APIstatus.idle)

	const setLoadingStatus = ()=>{
		setAPIStatus(APIstatus.loading)
		setError('')
	}

	const setErrorStatus = (error:string)=>{
		setAPIStatus(APIstatus.error)
		setError(error)
	}

	const setSuccessStatus = ()=>{
		setAPIStatus(APIstatus.success)
	}

	const createPaymentIntent = async (payload:CreatePaymentIntentPayload):Promise<PaymentIntentResponse | void>=>{
		setLoadingStatus()
		return await BillingAPI.createPaymentIntent(payload)
			.then((data)=>{
				setSuccessStatus()
				return data
			})
			.catch(()=>{
				const error =
				'There was an error creating your billing profile, please refresh the page'
				setErrorStatus(error)
			})
	}

	/**
	 * Creates a record of an existing stripe payment method
	 */
	const createPaymentMethod = async (payload: CreatePaymentMethodPayload)=> {
		setLoadingStatus()
		return await BillingAPI
			.createPaymentMethod(payload)
			.then((data)=>{
				setSuccessStatus()
				return data
			})
			.catch((err)=>{
				const error =
				err.message || 'There was an error creating your billing profile, please try again later'
				setErrorStatus(error)
			})
	}

	const processPayment = async ({
		paymentCustomer,
		customer,
		paymentMethod,
		amount,
	}:ProcessPaymentPayload) =>{
		setLoadingStatus()
		try{
			/**
			 * Creates a record of an existing stripe charge.
			 * 
			 * charge happens only on payment, hence why this
			 * isn't a helper function 
			 */
			await BillingAPI.createCharge({
				paymentCustomer,
				customer,
				paymentMethod,
				amount,
			})

			/**
			 * Stripe currently creates a payment method
			 * for a user on purchase, so we add a reference to it
			 * on our end
			 */
			await createPaymentMethod({
				paymentCustomer,
				customer,
				paymentMethod,
			})

			setSuccessStatus()
		}
		catch(err){
			/**
			 * If the above fails, the user was still charged,
			 * but we have no record of either a charge
			 * or/and payment method
			 */
			setErrorStatus('')
		}
	}

	const calculateBundlePrice = (cart:CartType)=>{
		return cart.lineItems.reduce((total:number, lineItem)=>{	
			let price = 0
			if(lineItem.product?.productType === 'recipe'){
				price = (lineItem.productVariant?.price || 0) * (lineItem.quantity || 0)
			}
			return round(total + price, 2)
		}, 0)
	}

	const getOrderSummary = 
	(
		children:Array<ChildrenType>,
		subscriptions:Record<string, CustomerSubscription>,
		carts: Record<string, any>
	):Array<OrderSummary>=>{
		const orderSummaries:Array<OrderSummary> = []
		children
			.filter(({id})=> {
				return subscriptions[id] && carts[id]
			})
			.forEach(({
				id,
				firstName,
			})=>{
				const {
					numberOfServings,
					frequency,
					customer,
				} = subscriptions[id]
				const cart:CartType = carts[id]
				const price = calculateBundlePrice(cart)

				orderSummaries.push({ 
					customerID: customer,
					cartID: cart.cartId,
					childID: id,
					title: `${firstName}'s Meal Plan`,
					description: `${numberOfServings} Meals • Every ${frequency} Weeks`,
					isMealPlan: true,
					price,
				})

				cart.lineItems.forEach((lineItem)=>{
					const product = lineItem.product as any as Product
					if(product.productType !== 'recipe'){
						const quantity = lineItem.quantity || 1
						orderSummaries.push({
							customerID: customer,
							productID: product.id,
							cartID: cart.cartId,
							childID: id,
							title: `${firstName}'s ${product.title}${lineItem.product?.showVariants ? ` (${lineItem.productVariant?.title })`: ''}`,
							description: `${quantity}x at $${lineItem.productVariant?.price}`,
							isMealPlan: false,
							price: (
								(lineItem.productVariant?.price || 0) * (lineItem.quantity as number)
							).toFixed(2),
						})
					}
				})

			})
		
		return orderSummaries
	}

	const getLatestPaymentMethod = async (customer: CustomerID):Promise<any> => {
		setLoadingStatus()
		try{
			const paymentMethod = await BillingAPI.getLatestPaymentMethod(customer)
			setSuccessStatus()
			return paymentMethod
		}
		catch(err){
			const error = 'There was an error loading your billing info, try again later'
			setErrorStatus(error)
			return err
		}
	}

	const applyDiscountCode = async (customer: CustomerID, discount: string):Promise<any> =>{
		setLoadingStatus()
		try{
			const data = await BillingAPI.applyDiscountCode({
				customer,
				discount,
			})
			setSuccessStatus()
			RenderSuccessToast(`${discount} succesfully applied 🎉`)
			return data
		}
		catch(err){
			RenderErrorToast(`"${discount}" is expired or invalid or is already applied`)
			const error = 'There was an error loading your billing info, try again later'
			setErrorStatus(error)
		}
	}

	const applyCancellationDiscount = async (discountPayload: CreateCancellationDiscountPayload):Promise<any> =>{
		setLoadingStatus()
		try{
			const data = await BillingAPI.applyDiscountCode(discountPayload)
			setSuccessStatus()
			
			return data
		}
		catch(err){
			setErrorStatus(error)
		}
	}

	return ({
		error,
		apiStatus,
		createPaymentIntent,
		createPaymentMethod,
		processPayment,
		getOrderSummary,
		getLatestPaymentMethod,
		applyDiscountCode,
		applyCancellationDiscount
	})
}

export default useBillingMethods
