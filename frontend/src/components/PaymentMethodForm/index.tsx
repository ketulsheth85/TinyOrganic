import React, { useEffect, useState } from 'react'
import { loadStripe } from '@stripe/stripe-js'
import {
	useStripe,
	useElements,
	Elements
} from '@stripe/react-stripe-js'
import useBillingMethods, { UseBillingMethods } from 'src/hooks/useBillingMethods'
import { SubscriptionSliceState } from 'store/subscriptionSlice'
import { RenderErrorToast } from 'components/Toast'
import PaymentForm from 'components/PaymentForm'
import { PaymentMethod } from 'api/BillingAPI/types'
import { GridLoader } from 'react-spinners'

const stripePromise = loadStripe(process.env.STRIPE_PUBLISHABLE_KEY as string)

export interface PaymentMethodForm{
	subscription: SubscriptionSliceState,
	onSubmitCallback?: (paymentMethod: Partial<PaymentMethod>)=> void
	cta?: string

}

const PaymentMethodFormHoc:React.FC<PaymentMethodForm> = ({
	subscription,
	onSubmitCallback,
	cta='Update Subscription'
})=>{
	const {
		id,

	} = subscription
	const [intentId, setIntentId] = useState<string>('')
	const [paymentCustomer, setPaymentCustomer] = useState<string>('')
	const [shouldRenderPaymentForm, setShouldRenderPaymentForm] = useState<boolean>(false)
	const billing = useBillingMethods()

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

	const createPaymentIntent = ()=>{
		billing.createPaymentIntent({
			customer: subscription.id,
			items: [{id: 'idhere'}, {id: 'idthere'}]
		})
			.then(async (data)=>{
				if(data){
					setIntentId(data.intent)
					setPaymentCustomer(data.paymentCustomer)
					setShouldRenderPaymentForm(true)	
				}
				else{ // if this is void, we assume we errored out
					RenderErrorToast('There was an error loading your payment profile, please try again later')
				}
			})
			.catch(()=>{
				RenderErrorToast('There was an error loading your payment profile, please try again later')
			})
	}

	useEffect(()=>{
		createPaymentIntent()
	}, [])


	if(!shouldRenderPaymentForm){
		return (
			<div className="flex justify-center margin-top-20">
				<GridLoader color='#204041' size={20} margin={4}/>
			</div>
		)
	}
	
	
	return (
		<div className="PaymentForm">
			{intentId && (
				<Elements 
					options={options} 
					stripe={stripePromise}>
					<PaymentMethodForm
						customer={id}
						billing={billing}
						paymentCustomer={paymentCustomer}
						onSubmitCallback={onSubmitCallback}
						cta={cta}
					/>
				</Elements>
			)}
		</div>
	)
}

interface PaymentMethodFormProps{
	customer: string
	billing: UseBillingMethods
	paymentCustomer: string
	onSubmitCallback: ((paymentMethod: Partial<PaymentMethod>) => void) | undefined
	cta?: string
}

const PaymentMethodForm:React.FC<PaymentMethodFormProps> = ({
	customer,
	billing,
	paymentCustomer,
	onSubmitCallback,
	cta,
})=>{

	const [submittingPaymentMethod, setSubmittingPaymentMethod] = useState(false)
	const [submittingPaymentMethodError, setSubmittingPaymentError] = useState('')
	const stripe = useStripe()
	const elements = useElements()

	const submitPaymentMethod = async () => {

		setSubmittingPaymentError('')
		setSubmittingPaymentMethod(true)
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
			setSubmittingPaymentError(message)
			setSubmittingPaymentMethod(false)
			return
		}

		if (setupIntent) {
			try{
				const paymentIntent = await billing.createPaymentMethod({
					paymentCustomer: paymentCustomer,
					paymentMethod: setupIntent.payment_method || '',
					customer: customer,
				})
				if(!paymentIntent){
					setSubmittingPaymentError('Error adding payment method, please try again')
				}

				if(onSubmitCallback && paymentIntent){
					onSubmitCallback(paymentIntent)
				}
			}
			catch(err){
				setSubmittingPaymentError('Error adding payment method, please try again')
			}
		}
		setSubmittingPaymentMethod(false)
	}

	return (
		<PaymentForm
			customer={customer}
			loading={submittingPaymentMethod}
			error={submittingPaymentMethodError}
			cta={cta}
			onSubmit={submitPaymentMethod}
		/>
	)
}

export default PaymentMethodFormHoc
