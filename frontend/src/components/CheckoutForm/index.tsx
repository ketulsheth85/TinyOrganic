import React, { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import {Row, Col} from 'antd'
import { 
	loadStripe,
} from '@stripe/stripe-js'
import {
	useStripe,
	useElements,
	Elements
} from '@stripe/react-stripe-js'

import { AppDispatch, dispatch, RootState } from 'store/store'
import { MultipageFormComponentProps } from 'src/shells/MultiPageForm'
import EditableInfoForm from 'src/shells/EditableInfoForm'
import AddressInfoForm from 'components/AddressInfoForm'
import AccountDetailsForm from 'components/AccountDetailsForm'
import PaymentForm from 'components/PaymentForm'
import OrderSummary, { RemoveItemPayload } from 'components/OrderSummary'
import useBillingMethods, { UseBillingMethods } from 'src/hooks/useBillingMethods'
import { isRejectedWithValue } from '@reduxjs/toolkit'

import { RenderErrorPage } from 'src/shells/ErrorBoundary'
import useOrderMethods from 'src/hooks/useOrderMethods'
import { useHistory } from 'react-router'
import { SplashPage } from 'components/OnboardingSplashPage'
import { ChildMealSelectionForm, ChildMealSelectionFormProps } from 'components/MealSelectionForm'
import { ChildrenType } from 'api/ChildrenAPI/types'
import {getChildrenCarts, updateCartLineItems} from 'store/cartSlice'
import { CreateCustomerSubscriptionPayload } from 'api/SubscriptionAPI/types'
import { createSubscription } from 'store/subscriptionSlice'
import { CartType } from 'api/CartAPI/types'
import { cloneDeep } from 'lodash'
import orderAPI from 'api/OrderAPI'
import { OrderSummaryType } from 'api/OrderAPI/types'
import analyticsClient from 'src/libs/analytics'
import { SHARE_A_SALE_COUPON_TO_ADD, SHARE_A_SALE_ORDERS_TO_TRACK, SHARE_A_SALE_ORDER_SUMMARY } from 'src/utils/constants'

import './styles.scss' 
import { segmentAnalitycs } from 'src/utils/utils'
import { CustomerAddress } from 'api/AddressAPI/types'

const stripePromise = loadStripe(process.env.STRIPE_PUBLISHABLE_KEY as string)
interface CheckoutFormProps{
	orderSummary: OrderSummaryType
	getOrderSummary: (discountCode?:string)=> Promise<void>
	paymentCustomer: string
	billing: UseBillingMethods
}
const CheckoutForm:React.FC<CheckoutFormProps> = ({
	orderSummary,
	paymentCustomer,
	getOrderSummary,
	billing
})=>{
	
	const store = useSelector((state:RootState)=> state.subscription)
	const {
		id,
		phoneNumber,
		addresses,
		subscriptions,
		hasPassword
	} = store

	const { subscription } = useSelector((state: RootState) => state)

	useEffect(()=>{
		analyticsClient.pageView('Onboarding', 'Checkout', {
			first_name: store.firstName,
			last_name: store.lastName,
			email: store.email
		})
		segmentAnalitycs('Checkout Step Viewed', {
			checkout_id:  subscription.id,
			step: 1,
			shipping_method: '',
			payment_method: ''
		})
		subscription.children.map((child: ChildrenType) => {
			const cart: CartType= carts.children[child.id]
			segmentAnalitycs('Checkout Started', {
				checkout_id:  subscription.id,
				currency: 'USD',
				shipping: orderSummary.shipping,
				discount: orderSummary.discounts,
				taxes: orderSummary.taxes,
				products: [
					cart.lineItems.map((lineItem: Record<any, any>) => {
						return {
							product_id: lineItem.product.id,
							name: lineItem.product.title,
							price: {
								value: lineItem.productVariant?.price,
								currency: 'USD',
							},
							quantity: lineItem.product.quantity,
							category: lineItem.product.productType,
							image_url: lineItem.product.imageUrl
						}
					})
				]
			})
		})
	},[])

	const hasFullAddress = (addresses: Array<CustomerAddress>)=>{
		if(addresses.length){
			const lastAddress = addresses[addresses.length-1]
			return (
				lastAddress.city && lastAddress.state && lastAddress.streetAddress && lastAddress.zipcode
			)
		}
	}

	useEffect(() => {dispatch(getChildrenCarts(id))}, [])
	const dispatch = useDispatch<AppDispatch>()
	const carts = useSelector((state:RootState)=> state.carts)
	const history = useHistory()

	/**
	 * If user hasn't filled out phone number, 
	 * they haven't seen this form before and
	 * we should show it
	 */
	const shouldShowAccountDetails = !phoneNumber || !hasPassword

	/**
	 * If user shouldn't see last form and has no addresses
	 * show this form
	 */
	const shouldOpenAddressForm = !shouldShowAccountDetails && !hasFullAddress(addresses)

	/**
	 * if user already filled out last form show this form 
	 */
	const shouldShowPaymentDetails = !!(phoneNumber && hasPassword && hasFullAddress(addresses))

	const [isOpenAccountDetails, setIsOpenAccountDetails] = useState(shouldShowAccountDetails)
	const [isOpenShippingDetails, setIsOpenShippingDetails] = useState(shouldOpenAddressForm)
	const [isOpenPaymentDetails, setIsOpenPaymentDetails] = useState(shouldShowPaymentDetails)
	const [mealPlanInfo, setMealPlanInfo] = useState({
		shouldRenderMealPlan: false,
		currentChild: ''
	})
	const stripe = useStripe()
	const elements = useElements()
	const orderHandler = useOrderMethods()
	const [startSubscriptionLoading, setStartSubcriptionLoading] = useState(false)
	const [startSubscriptionError, setStartSubcriptionError] = useState('')
	const [appliedDiscountCode, setAppliedDiscountCode] = useState('')

	const trackAccountInfoSubmit = () => {
		segmentAnalitycs('Checkout Step Completed', {
			checkout_id:  subscription.id,
			step: 1,
			shipping_method: '',
			payment_method: ''
		})
		segmentAnalitycs('Checkout Step Viewed', {
			checkout_id:  subscription.id,
			step: 2,
			shipping_method: '',
			payment_method: ''
		})
	}

	const trackShippingInfoSubmit = () => {
		segmentAnalitycs('Checkout Step Completed', {
			checkout_id:  subscription.id,
			step: 2,
			shipping_method: '',
			payment_method: ''
		})
		segmentAnalitycs('Checkout Step Viewed', {
			checkout_id:  subscription.id,
			step: 3,
			shipping_method: '',
			payment_method: ''
		})
	}

	const attentiveMobilePurchaseEvent = (_orderData: Record<any, any>) => {
		console.log('logging to attentive')
		const orderLineItems: Array<any> = []
		_orderData.orderLineItems.forEach((lineItem: Record<any, any>) => {
			orderLineItems.push({
				productId: lineItem.product.id,
				productVariantId: lineItem.productVariant?.skuId,
				name: lineItem.product.title,
				category: lineItem.product.productType,
				productImage: lineItem.product.imageUrl,
				price: {
					value: lineItem.productVariant?.price,
					currency: 'USD',
				},
				quantity: lineItem.quantity,
			})
		});
		(window as any).attentive.analytics.purchase({
			order: {
				orderId: _orderData.id,
				price: { value: _orderData.chargedAmount, currency: 'USD' }
			},
			user: {
				phone: store.phoneNumber,
				email: store.email,
			},
			cart: {
				cartId: carts.children[_orderData.customerChild].cartId,
			},
			items: orderLineItems,
		})
	}
	const onEditMealPlan = (childID:string)=>{
		setMealPlanInfo({
			shouldRenderMealPlan: true,
			currentChild: childID
		})
	}
	const onRemoveItem = ({childID, productID}:RemoveItemPayload) =>{
		const cart = cloneDeep(carts.children[childID]) as CartType
		for(let i = 0; i < cart.lineItems.length; i++){
			const item = cart.lineItems[i]
			if(item.product?.id === productID){
				item.quantity = 0
				break
			}
		}
		return dispatch(updateCartLineItems({
			customerId: id,
			cartId: cart.cartId,
			lineItems: cart.lineItems
		}))
			.then((action)=>{
				if(isRejectedWithValue(action)) return
				getOrderSummary()
			})
	}

	const startSubscription = async () => {
		setStartSubcriptionError('')
		setStartSubcriptionLoading(true)
		// disbable submission until stripe loads
		if (!stripe || !elements) {
			return
		}

		const { error, setupIntent } = await stripe.confirmSetup({
			elements,
			redirect: 'if_required',
		})
		
		if (error) {
			const message = (error.type === 'card_error' || error.type === 'validation_error') && error.message ||
			'We\'ve had an error processing your payment, please try again later'
			setStartSubcriptionError(message)
			setStartSubcriptionLoading(false)
			return
		}
		
		if (setupIntent) {
			/* Create payment intent in backend */
			const data = await billing.createPaymentMethod({
				paymentCustomer: paymentCustomer,
				paymentMethod: setupIntent.payment_method || '',
				customer: id,
			})
			
			if(!data || billing.error){
				setStartSubcriptionError(
					billing.error || 
					'We had an error processing your payment, please reload the page and try again.'
				)
				setStartSubcriptionLoading(false)
				return
			}
			if((window as any).analytics){
				(window as any).analytics.track('Added Payment Information', {
					customer_id: store.id,
					email: store.email,
					first_name: store.firstName,
					last_name: store.lastName,
				})
			}
			const childrenCarts: Array<string> = Object.entries(carts.children).map(([_, v]) => {
				// eslint-disable-next-line @typescript-eslint/ban-ts-comment
				// @ts-ignore
				return v.cartId as string
			})

			const orderData = await orderHandler?.createOrder({customer: id, carts: childrenCarts})

			if(!orderData || orderHandler.error){
				setStartSubcriptionError(
					orderHandler.error || 
					'We had an error processing your order, please reload the page and try again.'
				)
				setStartSubcriptionLoading(false)
				return
			}

			// TODO: Move tracking code to one method or section

			// do not remove semicolon, the code will break :crying_cat_face:
			if((window as any).analytics){
				(window as any).analytics.track('Purchase', {
					email: store.email,
					customer_id: store.id,
					first_name: store.firstName,
					last_name: store.lastName,
					phone_number: store.phoneNumber,
					currency: 'usd',
					value: orderSummary.total
				})

				if(orderData.length > 0) {
					orderData.map(order=>{
						segmentAnalitycs('Order Completed', {
							order_id: order.id,
							total: order.chargedAmount,
							currency: 'USD',
							shipping: orderSummary.shipping,
							discount: orderSummary.discounts,
							taxes: orderSummary.taxes,
							products: [
								order.orderLineItems.map((lineItem: Record<any, any>) => {
									return {
										product_id: lineItem.product.id,
										name: lineItem.product.title,
										price: {
											value: lineItem.productVariant?.price,
											currency: 'USD',
										},
										quantity: lineItem.product.quantity,
										category: lineItem.product.productType,
										image_url: lineItem.product.imageUrl
									}
								})
							]
						})
						segmentAnalitycs('Checkout Step Completed', {
							checkout_id:  subscription.id,
							step: 3,
							shipping_method: '',
							payment_method: ''
						})
					})
				}
			}
			if(orderData.length > 0) {
				const attentiveAnalytics = (window as any).attentive
				orderData.forEach((order) => {
					if(attentiveAnalytics) {
						attentiveMobilePurchaseEvent(order)
					}
				})
			}

			if ((window as any).gtag) {
				(window as any).gtag('event', 'purchase', {
					value: orderSummary.total,
					currency: 'USD',
					transaction_id: store.id,
					shipping: orderSummary.shipping,
					tax: orderSummary.taxes,
				})
			}

			if(orderData.length > 0){
				orderData.forEach((order)=>{
					(window as any).liQ = (window as any).liQ || [];
					(window as any).liQ.push({
						'event': 'conversion',
						'name': 'product_purchase',
						'email': store.email,
						'conversionId': order.id,
						'amount': order.chargedAmount,
						'currency': 'usd'
					})
				})
			}
			localStorage.setItem(SHARE_A_SALE_ORDERS_TO_TRACK, JSON.stringify(orderData))
			localStorage.setItem(SHARE_A_SALE_ORDER_SUMMARY, JSON.stringify(orderSummary))
			localStorage.setItem(SHARE_A_SALE_COUPON_TO_ADD, appliedDiscountCode)
			setStartSubcriptionLoading(false)
			history.push('/post-purchase')
		}		
	}

	if(mealPlanInfo.shouldRenderMealPlan){
		const child = store.children.find(({id})=> id === mealPlanInfo.currentChild) as ChildrenType
		const _subscription = subscriptions[mealPlanInfo.currentChild]
		const cart = carts.children[mealPlanInfo.currentChild]
		const onSubmit = (_cart:any)=> {

			dispatch(updateCartLineItems({
				cartId: _cart.cartId,
				customerId: id,
				lineItems: _cart.lineItems
			}))
				.then((action)=>{
					if(isRejectedWithValue(action)) return
					setMealPlanInfo({
						shouldRenderMealPlan: false,
						currentChild: ''
					})
					getOrderSummary()
				})
		}

		const onBack = ()=> setMealPlanInfo({
			shouldRenderMealPlan: false,
			currentChild: ''
		})

		const updateBundleInfo = (payload: CreateCustomerSubscriptionPayload) =>{
			return dispatch(createSubscription(payload))
		}

		return (
			<RenderMealPlan 
				title={`Editing ${child.firstName}'s Meal Plan`}
				updateBundleInfo={updateBundleInfo}
				analyticsInfo={{
					first_name: store.firstName,
					last_name: store.lastName,
					email: store.email
				}}
				apiStatus={carts.APIStatus}
				childCart={cart}
				currentChild={child}
				customer={store.id}
				childSubscription={_subscription}
				onSubmit={onSubmit}
				onBack={onBack}
			/>
		)
	}

	return (
		<div className="CheckoutForm">
			<h3 className="CheckoutForm__header">
					Checkout
			</h3>
			<div className="CheckoutForm__inner">
				<Row gutter={36}>
					<Col span={24}  lg={14}>
						<div className="CheckoutForm__details">
							<EditableInfoForm 
								title="1. Account Details"
								open={isOpenAccountDetails}
								details={[]}
								setOpen={shouldShowAccountDetails ? undefined : setIsOpenAccountDetails}
							>
								<AccountDetailsForm
									shouldSeeQuestion={()=>true} 
									className="OnboardingPageOverrides"
									passwordEditable
									store={store}
									onBack={
										shouldShowAccountDetails ? 
											undefined : (()=> setIsOpenAccountDetails(false))
									}
									onSubmit={()=>{
										trackAccountInfoSubmit()
										setIsOpenShippingDetails(true)
										setIsOpenAccountDetails(false)
									}}
								/>
							</EditableInfoForm>
							<EditableInfoForm 
								title="2. Shipping Address"
								open={isOpenShippingDetails}
								details={[]}
								setOpen={shouldShowAccountDetails ? undefined : setIsOpenShippingDetails}
							>
								<AddressInfoForm
									shouldSeeQuestion={()=>true}
									store={store}
									onBack={addresses.length === 0 ? undefined : ()=> setIsOpenShippingDetails(false)}
									onSubmit={()=> {
										trackShippingInfoSubmit()
										setIsOpenShippingDetails(false)
										setIsOpenPaymentDetails(true)
										getOrderSummary(appliedDiscountCode)
									}}
								/>
							</EditableInfoForm>
							<EditableInfoForm 
								title="3. Payment Method"
								open={isOpenPaymentDetails}
								details={[]}
								setOpen={!shouldShowPaymentDetails ? undefined : ()=> setIsOpenShippingDetails(false)}
							>
								<PaymentForm
									customer={id}
									loading={startSubscriptionLoading}
									error={startSubscriptionError}
									onSubmit={startSubscription}
								/>
							</EditableInfoForm>
						</div>
					</Col>
					<Col span={24} lg={10}>
						<OrderSummary
							onApplyDiscountCode={getOrderSummary}
							orderSummary={orderSummary}
							onRemoveItem={onRemoveItem}
							onEditMealPlan={onEditMealPlan}
							orders={billing.getOrderSummary(store.children, subscriptions, carts.children) || []}
							onSubmit={startSubscription}
							loading={startSubscriptionLoading}
							error={startSubscriptionError}
							disabled={!shouldShowPaymentDetails}
							appliedDiscountCode={appliedDiscountCode}
							setAppliedDiscountCode={setAppliedDiscountCode}
						/>
					</Col>
				</Row>
			</div>
		</div>
	)
}

const CheckoutFormHOC:React.FC<MultipageFormComponentProps> = ({
	shouldSeeQuestion
})=>{

	const {subscription, carts} = useSelector((state: RootState) => state)
	const [intentId, setIntentId] = useState<string>('')
	const [paymentCustomer, setPaymentCustomer] = useState<string>('')
	const billing = useBillingMethods()

	/**
	 * This component does not use the error, and apiStatus from billing
	 * because we only care about the payment intent being created. If
	 * we use the billing error and api status here, the page will show
	 * a loading screen for every api request and render the page useless
	 * if a one time errors occur
	 */
	const [error, setError] = useState('')
	const [loading, setLoading] = useState(true)
	
	const [orderSummary, setOrderSummary] = useState<OrderSummaryType>({
		subtotal: 0, discounts: 0, taxes: 0, shipping: 0, total: 0
	})
	const getOrderSummary = async (discountCode?:string)=>{
		return orderAPI.fetchOrderSummary(subscription.id, discountCode).then((data)=>{
			setOrderSummary(data)
		})
	}

	const init = async()=>{
		/**
		 * Check whether customer should be in this page
		 */
		const _shouldSeeQuestion = shouldSeeQuestion(`
			It looks like you haven't gotten to "Checkout" just yet,
			please fill out the form below to continue 😊
		`)
		if(!_shouldSeeQuestion) return

		const action = await dispatch(getChildrenCarts(subscription.id))
		if(isRejectedWithValue(action)){
			setError('There was an error loading the page, please try again later')
		}
		subscription.children.map((child: ChildrenType) => {
			// eslint-disable-next-line @typescript-eslint/ban-ts-comment
			// @ts-ignore
			const cart: CartType= carts.children[child.id]
			const lineItems = cart.lineItems;
			(window as any).gtag('event', 'begin_checkout', {
				items: lineItems.map((lineItem) => {
					return {
						id: lineItem.id,
						name: lineItem.product?.title,
						quantity: lineItem.quantity,
						price: lineItem.productVariant?.price,
						variant: lineItem.productVariant?.skuId,
					}
				}),
			})
		})

		if((window as any).analytics){
			(window as any).analytics.track('Initiate checkout', {
				first_name: subscription.firstName,
				last_name: subscription.lastName,
				email: subscription.email
			})
		}

		/**
		 * All is fine in the world :)
		 * Let's create a billing intent for my guy/girl/person and then
		 * render the checkout page
		 */
		billing.createPaymentIntent({
			customer: subscription.id,
			items: [{id: 'idhere'}, {id: 'idthere'}]
		})
			.then(async (data)=>{
				if(data){
					setIntentId(data.intent)
					setPaymentCustomer(data.paymentCustomer)
				}
				else{ // if this is void, we assume we errored out
					setError('There was an error creating your billing profile, please refresh the page')
				}
				return getOrderSummary()
			})
			.catch(()=>{
				setError('There was an error creating your billing profile, please refresh the page')
			})
			.finally(()=>{
				setLoading(false)	
			})
	}
	
	useEffect(() => {
		init()
	},[])



	if(error){
		return (
			<RenderErrorPage message={error} />
		)
	}

	if(loading){
		return <SplashPage/>
	}


	const options = {
		clientSecret: intentId,
		appearance: {
			theme: 'none' as any,
			variables: {
				colorPrimary: '#204041',
				colorBackground: '#fff',
				textColor: '#6B5C54'
			},
			rules:{
				'.Input':{
					color: '#5C696A',
					borderRadius: '5px',
					border: '1.5px solid #B2B8BD'
				},
				'.Input input':{
					paddingTop: '18px',
					paddingBottom: '18px'
				}
			}
		}
	}
	return (
		<div className="PaymentForm">
			{intentId && (
				<Elements 
					options={options} 
					stripe={stripePromise}>
					<CheckoutForm
						getOrderSummary={getOrderSummary}
						orderSummary={orderSummary}
						paymentCustomer={paymentCustomer}
						billing={billing}
					/>
				</Elements>
			)}
		</div>
	)
}

export default CheckoutFormHOC


const RenderMealPlan:React.FC<ChildMealSelectionFormProps> = (props)=>{
	return (
		<ChildMealSelectionForm
			{...props}
			backText="Cancel"
			submitText="Update Subscription"
		/>
	)
}
