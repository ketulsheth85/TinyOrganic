import { Customer } from 'api/CustomerAPI/types'
export type CustomerAddressBase = {
	id: string,
	customer: string
	streetAddress: string
	city: string
	state: string
	zipcode: string
	isActive: boolean
	validAddress?: boolean
	messages?: Array<string>
}

export type CustomerAddress = CustomerAddressBase & {
	validAddress?: boolean
	messages?: Array<string>
}

export type CustomerAddressCreationPayload = Partial<Omit<CustomerAddressBase, 'id' | 'isActive' >> & 
Pick<Customer, 'firstName' | 'lastName' | 'email'>

export type CustomerAddressUpdatePayload = Partial<CustomerAddressBase> & Pick<Customer, 'firstName' | 'lastName' | 'email'> & {
	id: string
	partial?: boolean
}
