import {useState} from 'react'

import DiscountAPI from 'api/DiscountAPI'
import { Discount } from 'api/DiscountAPI/types'
import { APIstatus } from 'store/types'
import { YOTPO_REFERRAL_LINK_BASE_URL } from 'src/utils/constants'


export interface UseDiscountMethods{
	error: string
	apiStatus: APIstatus
	getPrimaryDiscount:() => Promise<Discount | void>
	getReferralDiscount:() => Promise<Discount | void>
	getReferralLinkFromDiscount:(couponCode: Discount) => string
}

const useDiscountMethods = (): UseDiscountMethods =>{
	const [apiStatus, setApiStatus] = useState(APIstatus.idle)
	const [error, setError] = useState('')

	const setLoadingStatus = ()=>{
		setApiStatus(APIstatus.loading)
		setError('')
	}
	const setErrorStatus = (error:string)=>{
		setApiStatus(APIstatus.error)
		setError(error)
	}
	const setSuccessStatus = ()=>{
		setApiStatus(APIstatus.success)
	}

	const getPrimaryDiscount = async ()=>{
		setLoadingStatus()
		try{
			return await DiscountAPI
				.getPrimaryDiscount()
				.then((data)=>{
					setSuccessStatus()
					return data
				})
		}
		catch(err){
			setErrorStatus('Error loading banner discount')
		}
	}

	const getReferralDiscount = async ()=>{
		setLoadingStatus()
		try{
			return await DiscountAPI
				.getReferralDiscount()
				.then((data)=>{
					setSuccessStatus()
					return data
				})
		}
		catch(err){
			setErrorStatus('Error loading referral discount')
		}
	}

	/**
	 * Will return coupon link if link exists or an empty string otherwise
	 */
	const getReferralLinkFromDiscount = (coupon:Discount)=>{
		let couponCode = ''
		if(coupon?.fromYotpo){
			couponCode = `${YOTPO_REFERRAL_LINK_BASE_URL}/${coupon?.codename}`
		}
		return couponCode
	}

	return {
		error,
		apiStatus,
		getPrimaryDiscount,
		getReferralDiscount,
		getReferralLinkFromDiscount
	}
}

export default useDiscountMethods
