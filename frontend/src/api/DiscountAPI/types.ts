export type Discount = {
	id: string
	codename: string
	isActive: boolean
	isPrimary: boolean
	bannerText: string
	fromYotpo: boolean
}

export type GetDiscountPayload = {
	primary?: boolean,
	codename?: string
}
