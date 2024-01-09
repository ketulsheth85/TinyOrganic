import React, { useEffect, useState } from 'react'
import { useSelector } from 'react-redux'
import { Route, Switch, useHistory, useRouteMatch, } from 'react-router'
import { isRejectedWithValue } from '@reduxjs/toolkit'
import {AxiosError} from 'axios'

import Navigation, { NavigationLink } from 'components/Navigation'
import { dispatch, RootState } from 'store/store'
import DashboardInfoForm from 'components/DashboardInfoForm'
import DashboardPlanForm from 'components/DashboardPlanForm'
import { initStore as initSubscriptionState} from 'store/subscriptionSlice'
import {SplashPage} from 'components/OnboardingSplashPage'
import {RenderErrorPage} from 'src/shells/ErrorBoundary'
import { initStore as initCartStore} from 'store/cartSlice'
import { SubscriptionSliceState } from 'store/subscriptionSlice'
import { Modal, Button } from 'antd'
import { PaymentMethod } from 'api/BillingAPI/types'
import useBillingMethods from 'src/hooks/useBillingMethods'
import { get } from 'lodash'
import NoPaymentMethodModal from './components/NoPaymentModal'

import './styles.scss'
import DashboardAddonsForm from 'components/DashboardAddonsForm'
import { RenderSuccessToast } from 'components/Toast'
import DashboardReferralForm from 'components/DashboardReferralForm'


const DashboardPage:React.FC = ()=>{
	const {subscription, carts} = useSelector((state:RootState)=> state)
	const [renderRedirectModal, setRenderRedirectModal] = useState(false)
	const [renderNoPaymentMethodModal, setRenderNoPaymentMethodModal] = useState(false)
	const [paymentMethod, setPaymentMethod] = useState<Partial<PaymentMethod>>()
	const billingMethods = useBillingMethods()
	const {url} = useRouteMatch()
	const history = useHistory()
	const ROUTES = {
		plan:`${url}`,
		info: `${url}/my-info`.replace(/\/\//gi,'/'),
		referrals: `${url}/referrals`.replace(/\/\//gi,'/')
	}

	const onSubmitMissingPaymentInfo = (paymentMethod:Partial<PaymentMethod>) =>{
		setPaymentMethod(paymentMethod)
		setRenderNoPaymentMethodModal(false)
		RenderSuccessToast('Payment information succesfully added')
	}

	useEffect(()=>{
		dispatch(initSubscriptionState())
			.then((action)=>{
				const payload = action.payload as SubscriptionSliceState
				if(isRejectedWithValue(action) || !payload.id){
					return
				}

				// if(payload.status !== CustomerStatus.subscriber){
				// 	setRenderRedirectModal(true)
				// }

				dispatch((initCartStore(payload.id)))

				billingMethods
					.getLatestPaymentMethod(payload.id)
					.then((data)=>{
						if(data instanceof Error){
							const status = get((data as any as AxiosError), 'response.status')
							setRenderNoPaymentMethodModal(status === 404)
						}	
						else{
							setPaymentMethod(data as PaymentMethod)
						}
					})
			})
	},[])

	if(!subscription.init && subscription.error){
		return <RenderErrorPage>
			<h1>
				There was an error loading your profile, please try to reload the page or signing back in <a href="/accounts/login/"> here</a>
			</h1>

		</RenderErrorPage>
	}

	if(!subscription.init || !carts.init){
		return (
			<SplashPage />
		)
	}

	if(!subscription.id && subscription.error){
		return <RenderErrorPage 
			message="There was an error loading your profile, please try to reload the page" 
		/>
	}

	const logout = (e:any)=>{
		e.preventDefault()
		window.location.href = '/accounts/logout/'
	}

	const redirectToPlanPage = ()=>{
		history.push(ROUTES.plan)
	}

	const ADD_ONS_FORM_HEADER = 'Add-ons'
	const ADD_ONS_FORM_SUBTITLE = 'Yummy add-ons for the whole family. Note add-ons are one time purchases that are added to your next order(s)'
	
	return (
		<div className="DashboardPage">
			<Navigation>
				<NavigationLink href={ROUTES.plan}>
							My Plan
				</NavigationLink>
				<NavigationLink href={ROUTES.info}>
							My Info
				</NavigationLink>
				<NavigationLink href={ROUTES.referrals}>
							Referral
				</NavigationLink>
				<Button style={{marginTop: '-2px'}} type="primary" size="small" shape="round" onClick={logout}>
					Logout
				</Button>
			</Navigation>
			<div className="DashboardPage__body">
				<Switch>
					<Route exact path={`${url}`}>
						<DashboardPlanForm 
							carts={carts}
							subscription={subscription}
						/>
					</Route>
					<Route exact path={`${url}/add-ons`}>
						<DashboardAddonsForm
							title={ADD_ONS_FORM_HEADER}
							subtitle={ADD_ONS_FORM_SUBTITLE}
							carts={carts}
							subscription={subscription}
							onBack={redirectToPlanPage}
							onSubmit={redirectToPlanPage}
						/>
					</Route>
					<Route exact path={`${url}/my-info`}>
						<DashboardInfoForm 
							subscription={subscription}
							paymentMethod={paymentMethod}
							setPaymentMethod={setPaymentMethod}
							billingMethods={billingMethods}
						/>
					</Route>
					<Route exact path={`${url}/referrals`}>
						<DashboardReferralForm />
					</Route>
					{process.env.BRIGHTBACK_CANCELLATION_ENABLED && (
						<>
							<Route exact path={`${url}/cancellation_redemption`}>
								<DashboardPlanForm
									cancellationRedemption
									carts={carts}
									subscription={subscription}
								/>
							</Route>
							<Route exact path={`${url}/subscription_cancellation`}>
								<DashboardPlanForm
									subscriptionCancellation
									carts={carts}
									subscription={subscription}
								/>
							</Route>
						</>
					)}
				</Switch>
			</div>
			
			{renderRedirectModal && (
				<RedirectModal open={renderRedirectModal} />
			)}
			{renderNoPaymentMethodModal && (
				<NoPaymentMethodModal 
					open={renderNoPaymentMethodModal} 
					subscription={subscription}
					onSubmitCallBack={onSubmitMissingPaymentInfo}
				/>
			)}
		</div>
	)
}

export default DashboardPage

interface RedirectModalProps{
	open?: boolean 
}
const RedirectModal:React.FC<RedirectModalProps> = ({open})=>{
	const history = useHistory()
	const onContinueToOnboarding = ()=>{
		history.push('/onboarding/')
	}
	const onContactSupport = ()=>{
		history.push('/contact-support')
	}
	return (
		<Modal
			className="AddonsForm__modal"
			title="There was an issue loading your account"
			visible={open} 
			closable={false}
			footer={null}
		>
			Please make sure you have completed the onboarding and successfully
			checked out.
			<br/>
			If you have been charged for an order and cannot login,
			please contact support for more help.

			<div className="padding-top-14">
				<Button 
					shape="round"
					className="margin-right-8"
					onClick={onContinueToOnboarding} type="primary">
					Complete onboarding
				</Button>
				<Button shape="round" onClick={onContactSupport} type="default">
					Contact support
				</Button>
			</div>
		</Modal>
	)
}

