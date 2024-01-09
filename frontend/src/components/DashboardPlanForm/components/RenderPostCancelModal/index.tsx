import React from 'react'

import { TinyP } from 'components/Typography'

import TinyModal, { TinyModalProps } from 'src/shells/TinyModal'
import { APIstatus } from 'store/types'

export interface RenderPostCancelModalProps extends TinyModalProps{
	apiStatus: APIstatus
	transaction: 'cancellation' | 'couponRedemption'
}

const RenderPostCancelModal:React.FC<RenderPostCancelModalProps> = ({
	transaction,
	isModalVisible,
	apiStatus,
	onCancel
})=>{

	const getModalTitle = ()=>{
		let transactionTitle = 'Special Offer'
		if(transaction === 'cancellation'){
			transactionTitle = 'Subscription Cancellation'
		}
		return transactionTitle
	}


	const cancelSupportProps = React.useMemo(()=>{
		if(apiStatus === APIstatus.error){
			return {
				okText: 'Contact Support',
				onOk: ()=> {
					const _window = (window as any)
					_window.location = 'mailto:hello@tinyorganics.com'
					if(onCancel) onCancel()
				}
			}
		}
		return {
			okButtonProps: {
				style: {
					display: 'none'
				}
			}
		}
	}, [apiStatus])

	return (
		<TinyModal
			defaultFooter
			title={getModalTitle()}
			closable={false}
			isModalVisible={isModalVisible}
			onCancel={onCancel}
			cancelText="Close"
			cancelButtonProps={{ disabled: apiStatus === 'loading' }}
			maskClosable={false}
			{...cancelSupportProps}
		>
			<RenderPostCancelModalBody apiStatus={apiStatus} transaction={transaction}/>		
		</TinyModal>
	)
}

export interface RenderPostCancelModalBody{
	apiStatus: APIstatus
	transaction: 'cancellation' | 'couponRedemption'
}
const RenderPostCancelModalBody:React.FC<RenderPostCancelModalBody> = ({apiStatus, transaction})=>{
	if(apiStatus === APIstatus.success){
		if(transaction === 'cancellation'){
			return (
				<TinyP>
				Your subscription has been cancelled, we&apos;re sorry to see you go.
				</TinyP>
			)
		}
		return (
			<TinyP>
				Thanks for staying a part of our Tiny family!&nbsp;
				Your coupon has been added to your account and will be applied to your next order.
			</TinyP>
		)
	}
	
	if(apiStatus === APIstatus.error){
		if(transaction === 'cancellation'){
			return (
				<TinyP>
				There was an error cancelling your subscription. This might be because the subscription you intended to cancel has already been cancelled&nbsp;
				if this error persists, please contact support.
				</TinyP>
			)
		}
		return (
			<TinyP>
				There was an error applying this offer to your account, if this error persists, please contact support.
			</TinyP>
		)
	}

	return (
		<div>
			<TinyP>
				Please wait while we process your request...
			</TinyP>
		</div>
	)
}


export default RenderPostCancelModal
