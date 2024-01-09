import React, { useEffect, useState } from 'react'
import { 
	Button,
	Col
} from 'antd'
import {
	PaymentElement,
	useStripe,
	useElements,
} from '@stripe/react-stripe-js'
import { GridLoader } from 'react-spinners'
import {useDispatch} from 'react-redux'

import FormWrapper, { ButtonContainer } from 'src/shells/FormWrapper'
import { CustomerID } from 'api/CustomerAPI/types'
import {AppDispatch} from 'store/store'
import {getChildrenCarts} from 'store/cartSlice'
import { RenderErrorToast, RenderInfoToast, RenderSuccessToast } from 'components/Toast'

import './styles.scss'

export interface PaymentFormProps{
	customer: CustomerID,
	cta?: string
	loading?: boolean
	error?: string
	onSubmit: ()=> void
}
const PaymentForm:React.FC<PaymentFormProps> = ({
	customer,
	error,
	loading,
	cta = 'Start Subscription',
	onSubmit
})=> {
	const stripe = useStripe()
	const elements = useElements()
	const dispatch = useDispatch<AppDispatch>()
	const [stripeFormRendered, setStripeFormRendered] = useState(false)
	useEffect(() => {dispatch(getChildrenCarts(customer))}, [])
  
	useEffect(() => {
		if (!stripe) {
			return
		}

		const clientSecret = new URLSearchParams(window.location.search).get(
			'payment_intent_client_secret'
		)

		if (!clientSecret) {
			return
		}

		stripe.retrievePaymentIntent(clientSecret)
			.then(({ paymentIntent }) => {
				switch (paymentIntent?.status) {
				case 'succeeded':
					RenderSuccessToast('Payment succeeded!')
					break
				case 'processing':
					RenderInfoToast('Your payment is processing.')
					break
				case 'requires_payment_method':
					RenderErrorToast('Your payment was not successful, please try again.')
					break
				default:
					RenderErrorToast('Something went wrong.')
					break
				}
			})
	}, [stripe])

	if(!stripe || !elements){
		return (
			<RenderPaymentLoader />
		)
	}

	const onStripeFormRendered = ()=>{
		setStripeFormRendered(true)
	}

	return (
		<div className="PaymentForm">
			<FormWrapper className="OnboardingPageOverrides">
				<Col span={24}>
					<form>
						<PaymentElement id="payment-element" onReady={onStripeFormRendered}/>
						<br />
						{error && (
							<>
								<RenderPaymentDetailsMessage>
									{error}
								</RenderPaymentDetailsMessage>
								<br />
							</>
						)}
						{stripeFormRendered && (
							<ButtonContainer unstickyOnMobile>
								<Button
									onClick={onSubmit} 
									type="primary"
									size="large"
									htmlType="button"
									disabled={loading}
								>
									{cta}
								</Button>
							</ButtonContainer>
						)}
						{loading || !stripeFormRendered && (
							<RenderPaymentLoader />
						)}
					</form>
				</Col>
			</FormWrapper>
		</div>
	)
}

const RenderPaymentDetailsMessage = ({children}: {children: React.ReactChild})=>(
	<div className="ant-form-item-explain ant-form-item-explain-error">
		<div role="alert">
			{children}
		</div>
	</div>
)

const RenderPaymentLoader = ()=>(
	<div className="PaymentForm__loader">
		<GridLoader color='#204041' size={20} margin={4}/>
	</div>
)


export default PaymentForm
