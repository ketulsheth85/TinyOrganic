import API, { QueryArgsObj } from '..'
import { Product, RecommendedProducts } from './types'

const BACKEND_URL = '/api'

export class ProductAPI extends API {
	async getProducts(queryArgs?:QueryArgsObj):Promise<Array<Product>> {
		const args = this._queryArgs(queryArgs)
		return await this.client
			.get(`/v1/products/${args}`)
			.then((resp) => {
				return this._data(resp)
			})
	}

	async getProductsForChild(childId: string):Promise<RecommendedProducts> {
		return await this.client
			.get(`/v1/customers-children/${childId}/recommended_products/`)
			.then((resp) => {
				return this._data(resp)
			})
	}
}

export default new ProductAPI({
	baseURL: BACKEND_URL
})
