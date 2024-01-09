import React, { useEffect, useState } from 'react'
import { Col, Row } from 'antd'

import AccountDetailsForm from 'components/AccountDetailsForm'
import {EditableInfoFormCard} from 'src/shells/EditableInfoForm'
import { CustomerAddress } from 'api/AddressAPI/types'
import { STATE_REVERSE_HASH } from 'src/utils/constants'
import { SubscriptionSliceState } from 'store/subscriptionSlice'
import AddressInfoForm from 'components/AddressInfoForm'
import { PaymentMethod } from 'api/BillingAPI/types'
import { SplashPage } from 'components/OnboardingSplashPage'
import PaymentMethodForm from 'components/PaymentMethodForm'
import analyticsClient from 'src/libs/analytics'
import DiscountCodeForm from 'components/DiscountCodeForm'
import { UseBillingMethods } from 'src/hooks/useBillingMethods'

export interface PlanInfoFormProps{
	subscription: SubscriptionSliceState
	paymentMethod?: Partial<PaymentMethod>,
	setPaymentMethod: (paymentMethod: Partial<PaymentMethod>) => void
	billingMethods: UseBillingMethods
}
const DashboardInfoForm:React.FC<PlanInfoFormProps> = ({
	subscription,
	paymentMethod,
	setPaymentMethod,
	billingMethods
})=>{

	useEffect(()=>{
		analyticsClient.pageView('Dashboard', 'Customer Information', {
			first_name: subscription.firstName,
			last_name: subscription.lastName,
			email: subscription.email
		})
	}, [])

	const {
		id,
		addresses,
		firstName,
		lastName,
		email,
		phoneNumber
	} = subscription

	const [shouldRenderDashboardInfo, setShouldRenderDashboardInfo] = useState(false)
	const [isOpenAddressDetails, setIsOpenAddressDetails] = useState(false)
	const [isOpenAccountDetails, setIsOpenAccountDetails] = useState(false)
	const [isOpenPaymentMethodDetails, setIsOpenPaymentMethodDetails] = useState(false)

	useEffect(()=>{
		if(subscription.init){
			setShouldRenderDashboardInfo(true)
		}
	},[subscription.init])
	
	const displayCustomerAddress = (addresses: Array<CustomerAddress>)=>{
		if(addresses.length > 0){
			return [
				addresses[0].streetAddress,
				`${addresses[0].city}, ${STATE_REVERSE_HASH[addresses[0].state]} ${addresses[0].zipcode}`,
			]
		}
		return []
	}

	const updatePaymentSubscription = (paymentMethod:Partial<PaymentMethod>)=>{
		analyticsClient.updatedPaymentInformation({
			first_name: firstName,
			last_name: lastName,
			email: email
		})
		setPaymentMethod(paymentMethod)
		setIsOpenPaymentMethodDetails(false)
	}

	const applyDiscountCode = (code:string)=>{
		return billingMethods.applyDiscountCode(id,code)
	}

	const getPaymentMethodDetails = ()=>{
		if(paymentMethod){
			return [
				`Last Four: ${paymentMethod.lastFour}`,
				`Expiration Date ${paymentMethod.expirationDate}`
			]
		}
		return [
			'It looks like there was an error adding your payment information, please add your payment information to continue your subscription'
		]
	}

	const getPaymentMethodCTAButtonDetails = ()=>{
		if(paymentMethod){
			return 'Edit'
		}
		return 'Add Missing Payment Information'
	}

	const getUpdatePaymentMethodCTA = ()=>{
		if(paymentMethod){
			return 'Update Payment Method'
		}
		return 'Add Payment Method'
	}

	if(!shouldRenderDashboardInfo){
		return (
			<SplashPage />
		)
	}
	
	return (
		<Row>
			<Col span={24}>
				<EditableInfoFormCard
					title="Shipping Address"
					details={displayCustomerAddress(addresses)}
					open={isOpenAddressDetails}
					setOpen={setIsOpenAddressDetails}
				>
					<AddressInfoForm
						shouldSeeQuestion={()=>true}
						store={subscription}
						onBack={()=> setIsOpenAddressDetails(false)}
						onSubmit={()=>setIsOpenAddressDetails(false)}
					/>
				</EditableInfoFormCard>
				<EditableInfoFormCard
					title="Account Details"
					details={[
						`${firstName} ${lastName}`,
						email,
						`${phoneNumber}`
					]}
					open={isOpenAccountDetails}
					setOpen={setIsOpenAccountDetails}
				>
					<AccountDetailsForm
						shouldSeeQuestion={()=>true}
						className="OnboardingPageOverrides"
						store={subscription}
						onBack={()=> setIsOpenAccountDetails(false)}
						onSubmit={()=> setIsOpenAccountDetails(false)}
					/>
				</EditableInfoFormCard>	
				<EditableInfoFormCard
					title="Payment Method Details"
					details={getPaymentMethodDetails()}
					open={isOpenPaymentMethodDetails}
					setOpen={setIsOpenPaymentMethodDetails}
					onEditButtonCTA={getPaymentMethodCTAButtonDetails()}
				>
					<PaymentMethodForm
						onSubmitCallback={updatePaymentSubscription}
						subscription={subscription}
						cta={getUpdatePaymentMethodCTA()}
					/>
					
				</EditableInfoFormCard>
				<EditableInfoFormCard
					title="Have a discount code?"
					open={true}
					setOpen={()=>{/** */}}
					isEditable={false}
				>
					<DiscountCodeForm 
						onApplyDiscountCode={applyDiscountCode}
					/>
				</EditableInfoFormCard>
			</Col>
		</Row>
	)
}

export default DashboardInfoForm
