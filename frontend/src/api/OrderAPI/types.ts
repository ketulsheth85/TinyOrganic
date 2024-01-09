import { LineItemType } from 'api/CartAPI/types'
import {CustomerID} from 'src/api/CustomerAPI/types'

export type CartID = string

export type ShippingRateID = string

export type DiscountID = string

export type OrderCreationPayload = {
	customer: CustomerID,
	carts: Array<CartID>,
	shippingRate?: ShippingRateID
}

export type OrderSummaryType = {
	subtotal: number
	discounts: number
	shipping: number
	taxes: number
	total: number
}

export enum OrderFullfilmentStatus {
	pending = 'pending',
    partially_fulfilled = 'partial',
    fulfilled = 'fulfilled'
}

export enum OrderPaymentStatusEnum{
    pending = 'pending',
    failed = 'failed',
    authorized = 'authorized',
    partially_paid = 'partially_paid',
    paid = 'paid',
    partially_refunded = 'partially_refunded',
    refunded = 'refunded',
    voided = 'voided'
}

export enum FulfillmentStatus{
	pending = 'pending',
	partial = 'partial',
	fulfilled = 'fulfilled',
	cancelled = 'cancelled'
}

export type OrderType = {
	id: string,
	customerChild: string
	fulfillmentStatus: FulfillmentStatus
	paymentStatus: OrderFullfilmentStatus
	paymentMethod: string
	shippingRate?: ShippingRateID
	discount?: DiscountID
	orderLineItems: Array<LineItemType>
	externalOrderId?: string
	trackingNumber?: string
	chargedAt?:string
	orderNumber?: string
	chargedAmount?: string
}

export type OrderCreationResponse = Array<OrderType>

export type ShippingRatesResponse = {
	id: string,
	title: string,
	isActive: boolean
}

export type DiscountType = {
	id: string,
	codename: string
	isActive: boolean,
	isPrimary: boolean,
	bannerText: string
}

export type DiscountsResponse = Array<DiscountType>
