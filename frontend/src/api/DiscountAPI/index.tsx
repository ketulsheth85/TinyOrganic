import API, { QueryArgsObj } from '..'
import { Discount, GetDiscountPayload } from './types'

const BACKEND_URL = '/api'

export class DiscountAPI extends API {
	async getPrimaryDiscount(): Promise<Discount>{
		return this.client
			.get('/v1/discounts/?primary=true')
			.then((resp)=>{
				const discount = this._data(resp)
				if(discount.length){
					return discount[0]
				}
			})
	}

	async getDiscount(discountParams: GetDiscountPayload): Promise<Discount>{
		let params = ''
		if(Object.keys(discountParams).length > 0){
			params = this._queryArgs(discountParams as QueryArgsObj)
		}
		return this.client
			.get(`/v1/discounts/${params}`)
			.then((resp)=>{
				const discount = this._data(resp)
				if(discount.length){
					return discount[0]
				}
			})
	}
	async getReferralDiscount():Promise<Discount>{
		return this.client.
			get('/v1/discounts/customer/')
			.then((resp)=>{
				return this._data(resp)
			})
	}
}

export default new DiscountAPI({
	baseURL: BACKEND_URL
})
