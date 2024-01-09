import Sentry from '@sentry/browser'

import { 
	SHARE_A_SALE_COUPON_TO_ADD, 
	SHARE_A_SALE_ORDERS_TO_TRACK, 
	SHARE_A_SALE_ORDER_SUMMARY,
} from 'src/utils/constants'
import { OrderCreationResponse, OrderSummaryType } from 'api/OrderAPI/types'


interface UserShareASaleMembers{
	loadShareSaleParams: ()=> string
}

const useShareASaleMethods = ():UserShareASaleMembers =>{
	const _loadShareSaleParams = (
		parsedOrders: OrderCreationResponse, 
		orderSummary: OrderSummaryType,
		couponCode?: string)=>{
		const amount = `&amount=${orderSummary.subtotal - orderSummary.discounts}`
		const couponcode = couponCode ? `&couponCode=${couponCode}` : ''
		let tracking = '?tracking='
		let skuList = '&skulist='
		let priceList = '&pricelist='
		let quantityList = '&quantitylist='
		if(parsedOrders.length > 0){
			parsedOrders.forEach((order,i)=>{
				tracking += order.id
				if(i+1 < parsedOrders.length){
					tracking+='_'
				}
				order.orderLineItems.forEach((lineItem, j)=>{
					skuList += lineItem.productVariant?.skuId
					priceList += lineItem.productVariant?.price
					quantityList += lineItem.quantity
					if(j+1 < order.orderLineItems.length){
						skuList += ','
						priceList += ','
						quantityList += ','
					}
				})
			})
		}
		return tracking + amount + couponcode + priceList + quantityList + skuList
	}
	
	const loadShareSaleParams = ()=>{
		const orders = localStorage.getItem(SHARE_A_SALE_ORDERS_TO_TRACK)
		const couponCode = localStorage.getItem(SHARE_A_SALE_COUPON_TO_ADD) || undefined
		const orderSummary = localStorage.getItem(SHARE_A_SALE_ORDER_SUMMARY)
		let params = ''
		try{
			if(orders){
				const parsedOrders = JSON.parse(orders)
				const parsedOrderSummary = JSON.parse(orderSummary || '{}')
				params = _loadShareSaleParams(parsedOrders, parsedOrderSummary, couponCode)
			}
		}
		catch(err){
			/**
			 * This method is only used when a purchase is made, so we want to still
			 * checkout even if we can't track a referral purchase
			 */
			Sentry.captureException(err)
		}
		localStorage.removeItem(SHARE_A_SALE_ORDERS_TO_TRACK)
		localStorage.removeItem(SHARE_A_SALE_COUPON_TO_ADD)
		localStorage.removeItem(SHARE_A_SALE_ORDER_SUMMARY)
		return params
	}
	
	return {
		loadShareSaleParams
	}
}

export default useShareASaleMethods
