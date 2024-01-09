import { CustomerAddress } from 'api/AddressAPI/types'
import { ChildrenType } from 'api/ChildrenAPI/types'

export enum GuardianType {
	parent = 'parent',
	parent_and_expecting = 'parent_and_expecting',
	caregiver = 'caregiver',
	expecting = 'expecting',
	other = 'other'
}

export enum CustomerStatus {
	lead = 'lead',
	plan_selection = 'plan_selection',
	checkout = 'checkout',
	subscriber = 'subscriber',
	deactivated = 'deactivated'
}

export type Customer ={
	id: CustomerID
	PaymentProviderID?: string
	firstName: string
	lastName: string
	email: string
	phoneNumber?: string
	status: CustomerStatus
	guardianType: GuardianType
	hasActiveSubscriptions: boolean
	hasPassword: boolean
	children: Array<ChildrenType>
	addresses: Array<CustomerAddress>
	token?: string
}

export type CustomerCreationPayload = Pick<Customer, 'firstName' | 'lastName' | 'email'> & Pick<CustomerAddress, 'zipcode'>

export type CustomerID = string

export type CustomerUpdatePayload = Partial<Customer>

export type AddCustomerDetailsPayload = Partial<Customer> & {password: string}
