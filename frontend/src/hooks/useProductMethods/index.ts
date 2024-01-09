import {useState} from 'react'
import { toast } from 'react-toastify'

import ProductsAPI from 'src/api/ProductsAPI'
import { Product, RecommendedProducts } from 'api/ProductsAPI/types'
import { APIstatus } from 'store/types'

export interface UseProductMethodsProps{
	init: boolean,
	APIStatus: APIstatus,
	error: string,
	getProducts: (queryArgs?: Record<string, string | number>)=> Promise<Array<Product>>
	getProductsForChild: (childId: string) => Promise<RecommendedProducts>
}

const useProductMethods = (): UseProductMethodsProps=>{

	const [init, setInit] = useState<boolean>(false)
	const [apiStatus, setAPIStatus] = useState<APIstatus>(APIstatus.idle)
	const [error, setError] = useState<string>('')

	const setLoadingStatus = ()=>{
		setAPIStatus(APIstatus.loading)
		setError('')
	}
	const setErrorStatus = (error:string)=>{
		toast.error(error)
		setAPIStatus(APIstatus.error)
		setError(error)
	}

	const setSuccessStatus = ()=>{
		setError('')
		setAPIStatus(APIstatus.success)
	}

	const getProductsForChild = async (childId: string): Promise<RecommendedProducts> => {
		setLoadingStatus()
		return ProductsAPI.getProductsForChild(childId).then((data) => {
			setSuccessStatus()
			setInit(true)
			return data as RecommendedProducts
		}).catch(
			() => {
				const error = 'There was an error loading products, please try reloading the page'
				setErrorStatus(error)
				return {
					tinyBeginnings: [],
					recommendations: [],
					remainingProducts: []
				}
			}
		)
	}

	const getProducts = async (queryArgs?:Record<string, string | number>): Promise<Array<Product>> => {
		setLoadingStatus()
		return ProductsAPI.getProducts(queryArgs)
			.then((data)=>{
				setSuccessStatus()
				setInit(true)
				return data as Array<Product>
			})
			.catch(()=>{
				const error = 'There was an error loading products, please try reloading the page'
				setErrorStatus(error)
				return [] as Array<Product>
			})
	}

	return ({
		init,
		APIStatus: apiStatus,
		error,
		getProducts,
		getProductsForChild,
	})
}

export default useProductMethods
