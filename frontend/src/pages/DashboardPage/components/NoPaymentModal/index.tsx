import React from 'react'
import {Modal} from 'antd'

import { SubscriptionSliceState } from 'store/subscriptionSlice'
import PaymentMethodForm from 'components/PaymentMethodForm'
import { PaymentMethod } from 'api/BillingAPI/types'

import './styles.scss'

interface NoPaymentMethodModalProps{
	open?: boolean 
	subscription: SubscriptionSliceState,
	onSubmitCallBack: (paymentMethod: Partial<PaymentMethod>) => void
}
const NoPaymentMethodModal:React.FC<NoPaymentMethodModalProps> = ({
	open, 
	subscription,
	onSubmitCallBack
})=>{
	return (
		<Modal
			className="NoPaymentMethodModal AddonsForm__modal"
			title="Missing Payment Information"
			visible={open} 
			closable={false}
			footer={null}
		>
			<p>
				We could not find a valid payment method for this account.
				To prevent a <strong>delay for future orders</strong>,
				please add a new payment method below.
			</p>

			<PaymentMethodForm
				onSubmitCallback={onSubmitCallBack}
				subscription={subscription}
				cta={'Add Payment Information'}
			/>
		</Modal>
	)
}

export default NoPaymentMethodModal
