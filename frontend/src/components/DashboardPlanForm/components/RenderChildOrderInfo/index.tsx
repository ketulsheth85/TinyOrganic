import React, { useState } from 'react'
import { isRejectedWithValue } from '@reduxjs/toolkit'
import { Button, Col, Row } from 'antd'

import { OrderType } from 'api/OrderAPI/types'
import { CustomerPrecancelURL, CustomerSubscriptionStatus } from 'api/SubscriptionAPI/types'
import { RenderErrorToast, RenderSuccessToast } from 'components/Toast'

import { EditableInfoFormCard } from 'src/shells/EditableInfoForm'
import TinyModal from 'src/shells/TinyModal'
import { CartSliceState } from 'store/cartSlice'
import { dispatch } from 'store/store'
import { cancelSubscription, preCancelSubscription, SubscriptionSliceState } from 'store/subscriptionSlice'
import RenderChildWithSubscription from '../RenderChildWithSubscription'
import RenderChildOrderInfoViewController from './vc'
import RenderAddonsBanner from '../RenderAddonsBanner'

export interface RenderChildOrderInfoProps{
	subscription: SubscriptionSliceState
	carts: CartSliceState
	orders: Record<string, OrderType>
}
const RenderChildOrderInfo:React.FC<RenderChildOrderInfoProps> = ({
	subscription,
	carts,
	orders
})=>{
	
	const renderChildOrderInfoViewController = RenderChildOrderInfoViewController(
		subscription,
		orders,
		carts
	)

	const childrenWithSubcriptions = subscription.children
		.filter(({id})=>{
			return carts.children[id] && subscription.subscriptions[id]
		})

	const childrenWithActiveSubscriptions = childrenWithSubcriptions.filter(({id})=> (
		subscription.subscriptions[id].status === CustomerSubscriptionStatus.active
	) )

	return (
		<Row>
			<Col span={24}>
				<RenderChildWithSubscription
					childrenWithSubcriptions={childrenWithSubcriptions}
					renderChildOrderInfoViewController={renderChildOrderInfoViewController}
				/>
			</Col>
			<Col span={24}>
				<RenderAddonsBanner />
			</Col>
			{childrenWithActiveSubscriptions.length > 0 && (
				<Col span={24} style={{marginTop: 300}}></Col>
			)}
			<Col span={24}>
				<Row gutter={16}>
					{
						childrenWithActiveSubscriptions.map(({id,firstName})=>{
							return (
								<RenderChildOrderInfoItem
									key={`RenderChildOrderInfoItem-${id}`}
									subscription={subscription}
									child={id}
									firstName={firstName}
								/>
							)
						})
					}
				</Row>
			</Col>
		</Row>
	)
}

interface RenderChildOrderInfoItemProps{
	subscription: SubscriptionSliceState
	firstName: string,
	child: string
}

const RenderChildOrderInfoItem:React.FC<RenderChildOrderInfoItemProps> = ({
	firstName,
	child,
	subscription
})=>{
	const [renderCancelModal, setRenderCancelModal] = useState(false)

	const openModal = ()=> setRenderCancelModal(true)
	const closeModal = ()=> setRenderCancelModal(false)
	const preCancelChildSubscription = ()=>{
		const childSubscription = subscription.subscriptions[child]
		dispatch(preCancelSubscription(childSubscription.id))
			.then((action)=>{
				if(isRejectedWithValue(action)){
					RenderErrorToast('There was an error cancelling your subscription, please try again later')
					return
				}
				const payload = action.payload as CustomerPrecancelURL
				const redirectURL = payload.url
				window.location.href = redirectURL
			})
	}
	const sadlyCancelChildSubscription = ()=>{
		const childSubscription = subscription.subscriptions[child]
		dispatch(cancelSubscription(childSubscription.id))
			.then((action)=>{
				if(isRejectedWithValue(action)){
					RenderErrorToast('There was an error cancelling your subscription, please try again later')
					return
				}
				RenderSuccessToast('Subscription successfully canceled')
				closeModal()
			})
	}

	/**
	 * Temp function that will call precancel flow if enabled
	 */
	const onClickCancellation = ()=>{
		let callback = openModal
		if(process.env.BRIGHTBACK_CANCELLATION_ENABLED){
			callback = preCancelChildSubscription
		}
		callback()
	}
	const title = `Cancel ${firstName}'s Subscription`

	return (
		<Col span={24} md={12} key={`subscription-cancel-card-${child}`}>
			<EditableInfoFormCard
				title={title}
				open={true}
				setOpen={()=> {/** */}}
				isEditable={false}
			>
				<div className="margin-top-20">
					<strong>Note:</strong> orders for which you have been charged prior to 
					cancellation will remain active and ship as scheduled.
					<div>
						<Button 
							type="text"
							onClick={onClickCancellation}
							className="margin-top-8 padding-left-0"
						>
						Cancel Subscription
						</Button>
					</div>
				</div>
				<TinyModal
					title={`
						Are you sure you want to cancel ${firstName}'s
						subscription?
					`}
					isModalVisible={renderCancelModal}
					onCancel={closeModal}
					footer={null}
				>
					Cancelling your subscription means that {firstName}&nbsp;
					will no longer receive healthy,
					and delicious meals from Tiny Organics.

					<div className="padding-top-20">
						<Button 
							className="margin-right-8"
							shape="round" 
							onClick={closeModal} 
							type="primary">
							Continue Subscription 🎉
						</Button>
						<Button
							className="padding-0" 
							shape="round"
							onClick={sadlyCancelChildSubscription} 
							type="default" 
							size="small">
								Cancel Subscription 😿
						</Button>
					</div>
				</TinyModal>
			</EditableInfoFormCard>
		</Col>
	)
}


export default RenderChildOrderInfo
