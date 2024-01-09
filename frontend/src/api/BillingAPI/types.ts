import {CustomerID} from 'src/api/CustomerAPI/types'

export type StripeCustomerID = string

export type CreatePaymentIntentPayload = {
	customer: CustomerID
	items: Array<Product>
}

export type PaymentIntentResponse = {
	intent: string
	paymentCustomer: string
}

export type Product = {
	id: ProductSKU
}

export type CreateChargePayload = {
	paymentCustomer: string
	customer: CustomerID
	paymentMethod: string
	amount: number
}

export type ProductSKU = string

export type CreatePaymentMethodPayload = {
	paymentCustomer: string
	customer: CustomerID
	paymentMethod: string
}

export type Charge = {
	id?: string
	customer: CustomerID
	amount: number
}

export type PaymentMethod = {
	id?: string
	paymentCustomer: StripeCustomerID
	customer: CustomerID
	paymentMethod: string
	lastFour: number
	expirationDate: string
}

export type CreateCustomerDiscountPayload = {
	customer: CustomerID,
	discount: string,
	session?: string,
	subscription?: string
}

export type CreateCancellationDiscountPayload = CreateCustomerDiscountPayload & {
	session: string,
	subscription: string
}
