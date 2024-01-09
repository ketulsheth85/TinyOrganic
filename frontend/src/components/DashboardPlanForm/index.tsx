import React, { useEffect } from 'react'

import { CartSliceState } from 'store/cartSlice'
import { RenderErrorPage } from 'src/shells/ErrorBoundary'
import { SplashPage } from 'components/OnboardingSplashPage'
import RenderChildOrderInfo from './components/RenderChildOrderInfo'
import { SubscriptionSliceState } from 'store/subscriptionSlice'
import analyticsClient from 'src/libs/analytics'
import RenderPostCancelModal from './components/RenderPostCancelModal'
import vc from './vc'

import './styles.scss'

export interface DashboardPlanFormProps{
	cancellationRedemption?: boolean
	subscriptionCancellation?: boolean
	subscription: SubscriptionSliceState
	carts: CartSliceState
}
const DashboardPlanForm:React.FC<DashboardPlanFormProps> = ({
	subscriptionCancellation,
	cancellationRedemption,
	subscription,
	carts,
})=>{

	/**
	 * Keeping this outside of view controller as analytics have been flaky and
	 * this works
	 */
	const registerPageView = ()=>{
		analyticsClient.pageView('Dashboard', 'Subscription Plan Page',{
			first_name: subscription.firstName,
			last_name: subscription.lastName,
			email: subscription.email
		})
	}

	useEffect(()=>{
		if(cancellationRedemption){
			actions.redeemCancellationCoupon(subscription.id)
		}
		if(subscriptionCancellation){
			actions.cancelUserSubscription()
		}
		else{
			registerPageView()
		}
		
	},[])


	const {
		postCancellationAPIStatus,
		showPostCancellationModal,
		loading,
		orders,
		renderErrorPage,
		actions
	} = vc({
		subscriptionCancellation,
		cancellationRedemption
	})

	useEffect(()=>{
		const customer = subscription.id
		const childIds = subscription.children.map(({id})=> id)
		actions.init(customer, childIds)
	}, [])

	if(loading){
		return <SplashPage />
	}
	
	if(renderErrorPage){
		return <RenderErrorPage 
			message={actions.orderMethods.error}
		/>
	}

	
	return (
		<div className="DashboardPlanForm">
			<RenderChildOrderInfo 
				subscription={subscription} 
				carts={carts}
				orders={orders}
			/>
			<RenderPostCancelModal 
				apiStatus={postCancellationAPIStatus}
				transaction={actions.cancellationTransactionType}
				isModalVisible={showPostCancellationModal}
				onCancel={actions.onCloseCancellationModal}
			/>
		</div>
	)
}

export default DashboardPlanForm
