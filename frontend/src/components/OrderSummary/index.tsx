import React, { useEffect, useState } from 'react'
import { Button } from 'antd'
import { isRejectedWithValue } from '@reduxjs/toolkit'

import { RenderErrorToast, RenderInfoToast, RenderSuccessToast } from 'components/Toast'
import { MealIcon, VegetableIcon } from 'components/svg'
import { OrderSummary as billingOrderSummary } from 'src/hooks/useBillingMethods'
import { OrderSummaryType } from 'api/OrderAPI/types'
import { TinyP } from 'components/Typography'
import {useSelector} from 'react-redux'
import {RootState} from 'store/store'

import './styles.scss'

interface OrderSummaryProps {
	orderSummary: OrderSummaryType
	loading?: boolean
	orders: Array<billingOrderSummary>
	error?: string
	disabled?: boolean
	onEditMealPlan: (childID:string)=> void
	onRemoveItem: (payload: RemoveItemPayload) => Promise<any>
	onApplyDiscountCode: (discountCode: string) => Promise<any>
	appliedDiscountCode?: string
	setAppliedDiscountCode: (discountCode: string) => void
	onSubmit: ()=> void
}

const OrderSummaryComponent:React.FC<OrderSummaryProps> = ({
	orderSummary,
	orders,
	onSubmit,
	loading,
	error,
	onEditMealPlan,
	onRemoveItem,
	disabled,
	onApplyDiscountCode,
	appliedDiscountCode,
	setAppliedDiscountCode
})=>{

	useEffect(()=>{
		if(error){
			RenderErrorToast(error)
		}
	}, [error])

	const [discountCode, setDiscountCode] = useState('')
	const store = useSelector((state:RootState)=> state.subscription)
	const _setDiscountCode = (e:any)=>{
		setDiscountCode(e.target.value)
	}

	const _onApplyDiscountCode = ()=>{
		if(discountCode.length === 0) return
		onApplyDiscountCode(discountCode)
			.then(()=>{
				if((window as any).analytics){
					(window as any).analytics.track('Added Discount Code to Initial Order',
						{
							discountCode,
							email: store.email,
							customer_id: store.id,
							first_name: store.firstName,
							last_name: store.lastName,
						})
				}
				RenderSuccessToast(`"${discountCode}" applied`)
				setAppliedDiscountCode(discountCode)
				setDiscountCode('')
			})
			.catch(()=>{
				RenderErrorToast(`"${discountCode}" is expired or invalid`)
			})
	}

	return (
		<div className="CheckoutSummary">
			<div className="CheckoutSummary__inner">
				<h3 className="CheckoutSummary__title">
				Order Summary
				</h3>
				<RenderItems 
					orderSummary={orders}
					onEditMealPlan={onEditMealPlan}
					onRemoveItem={onRemoveItem}
				/>
				<div className="CheckoutSummary__input">
					<h5 className="CheckoutSummary__input-label">
					Have a promo code?
					</h5>
					<div className="CheckoutSummary__input-inner" 
						style={{
							marginBottom: 16
						}}
					>
						<input 
							value={discountCode} 
							onChange={_setDiscountCode} 
							type="text" 
							placeholder="Enter Promo Code"
						/>
						<button onClick={_onApplyDiscountCode}>APPLY</button>
					</div>
					{appliedDiscountCode && (
						<TinyP 
							className={`
							color-deep-ocean
							font-16
							weight-300
						`}>
							{`"${appliedDiscountCode}" applied 😎`}
						</TinyP>
					)}
				</div>
				<RenderBreakDown orderSummary={orderSummary}/>
				<Button
					className="CheckoutSummary__checkout-btn"
					type="primary"
					size="large"
					shape="round"
					onClick={onSubmit}
					loading={loading}
					disabled={disabled || loading}
				>
					Start Subscription
				</Button>
				<p className="CheckoutSummary__remark">
					Change or cancel your plan at any time!
				</p>
				<p className="CheckoutSummary__disclosure">
					By placing your order, you agree to our{' '}
					<a style={{
						color: 'blue !important',
						marginRight: '5px !important'
					}} href="https://www.tinyorganics.com/pages/terms-and-conditions" target="_blank" rel="noreferrer"> 
						Terms and Conditions.{' '}
					</a>
					Your first order will process immediately and ship out within 2-4 business days. 
					Your next order will process according to your selected order frequency.
				</p>
			</div>
		</div>
	)
}

export interface RemoveItemPayload{
	childID: string
	productID: string
}

export interface RenderItemsProps{
	orderSummary: Array<billingOrderSummary>
	onEditMealPlan: (childID: string) => void
	onRemoveItem: (payload:RemoveItemPayload) => Promise<any>
}
const RenderItems:React.FC<RenderItemsProps> = ({
	orderSummary,
	onEditMealPlan,
	onRemoveItem
})=>{
	const renderIcon = (isMealPlan:boolean) =>{
		if(isMealPlan){
			return <MealIcon width={47} height={35}/>
		}
		else{
			return <VegetableIcon width={47} height={35}/>
		}
	}

	/**
	 * Note that this will only work for non recipe order summaries
	 * as items of type recipe are bundled and showed in the order summary
	 * as one object and don;t actually have a product id
	 */
	const _onRemoveItem = (childID:string, productID:string, productTitle:string)=>{
		onRemoveItem({
			childID,
			productID,
		})
			.then((action)=>{
				if(isRejectedWithValue(action)){
					return
				}
				RenderInfoToast(`${productTitle} removed`)
			})
	}
	console.log('orderSummary ', orderSummary)
	return (
		<div className="CheckoutSummary__item-container">
			{orderSummary.map(({
				productID,
				cartID,
				title,
				childID,
				description,
				isMealPlan,
				price
			})=>{
				const cta = isMealPlan ? 'Edit Meal Plan' : 'Remove'
				const getOnClickHandler = (isMealPlan: boolean)=>{
					if(isMealPlan){
						return ()=> onEditMealPlan(childID)
					}
					return ()=> _onRemoveItem(childID, productID as string, title)
				}
				return (
					<div key={cartID+childID+title} className="CheckoutSummary__item">
						<div className="CheckoutSummary__item-icon">
							{renderIcon(isMealPlan)}
						</div>
						<div className="CheckoutSummary__details">
							<p className="CheckoutSummary__item-name">
								{title}
							</p>
							<p className="CheckoutSummary__item-description">
								{description}
							</p>
							<button
								onClick={getOnClickHandler(isMealPlan)}
								className="CheckoutSummary__button"
							>
								{cta}
							</button>
						</div>
						<div className="CheckoutItem__price">
							<p>${price}</p>
						</div>
					</div>
				)
			})}
		</div>
	)
}

interface RenderBreakDownProps{
	orderSummary: OrderSummaryType
}
const RenderBreakDown:React.FC<RenderBreakDownProps> = ({orderSummary})=>{
	const {
		subtotal,
		discounts,
		shipping,
		taxes,
		total
	} = orderSummary
	return (
		<>
			{
				Object.keys(orderSummary).length > 0 && (
					<>
						<div className="CheckoutSummary__breakdown">
							<div className="CheckoutSummary__breakdown-line">
								<p>Subtotal</p>
								<p>{subtotal.toFixed(2)}</p>
							</div>
							<div className="CheckoutSummary__breakdown-line">
								<p>Discount</p>
								<p>
									{discounts > 0 && '-'}
									{discounts.toFixed(2)}
								</p>
							</div>
							<div className="CheckoutSummary__breakdown-line">
								<p>Shipping &amp; Handling</p>
								<p>{shipping.toFixed(2)}</p>
							</div>
							{taxes > 0 && (
								<div className="CheckoutSummary__breakdown-line">
									<p>Tax</p>
									<p>{taxes.toFixed(2)}</p>
								</div>
							)}
						</div>
						<div className="CheckoutSummary__breakdown-line CheckoutSummary__breakdown--bold">
							<p>Today&apos;s Total</p>
							<p>{total.toFixed(2)}</p>
						</div>
					</>
				)
			}
		</>
	)
}

export default OrderSummaryComponent
