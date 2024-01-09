import { CustomerAddressBase } from 'api/AddressAPI/types'
import { ChildrenID } from 'api/ChildrenAPI/types'
import { CustomerID } from 'src/api/CustomerAPI/types'

export enum CustomerSubscriptionStatus{
	active = 'active',
	inactive = 'inactive'
}

export type CustomerSubscription = {
	id: string
	firstName: string
	lastName: string
	addresses: Array<CustomerAddressBase>
	email: string
	customer: CustomerID
	customerChild: ChildrenID
	numberOfServings: number
	frequency: number
	isActive: boolean
	status: CustomerSubscriptionStatus
	activatedAt?: string
	deactivatedAt?: string
	nextOrderChargeDate?: string
	nextOrderChangesEnabledDate?: string
	isNew?: boolean
}

export type CustomerSubscriptionCreationResponse = CustomerSubscription & {token: string}

export type UpdateCustomerSubscriptionChargeDatePayload = {
	subscription: string
	nextOrderChargeDate: string
}

export type CreateCustomerSubscriptionPayload = 
Pick<
	CustomerSubscription, 
	'customer' | 'customerChild' | 'frequency' | 'numberOfServings'
>


export type CustomerPrecancelURL = {
	url: string
}
