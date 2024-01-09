import { Discount } from 'api/DiscountAPI/types'
import { useMemo, useState } from 'react'
import useDiscountMethods from 'src/hooks/useDiscountMethods'


type DashboardReferralFormlViewControllerFields = {
	loading: boolean
	pageLoading: boolean
	referralCode: string
	referralBannerImage: string
}

type DashboardReferralFormlViewControllerMethods = {
	init: ()=> void
	getReferralLinkFromDiscount: () => string
}

export type DashboardReferralFormlViewControllerMembers = {
	fields: DashboardReferralFormlViewControllerFields
	actions: DashboardReferralFormlViewControllerMethods
}

const useDashboardReferralFormViewController = ():DashboardReferralFormlViewControllerMembers =>{

	const [pageLoading, setPageloading] = useState(true)
	const [discountCode, setDiscountCode] = useState<Discount>()
	const referralCode = useMemo(()=>{
		if(!discountCode){
			return ''
		}
		return discountCode.codename
	}, [discountCode])
	const [loading, setLoading] = useState(false)
	const REFERRAL_BANNER_IMAGE = 'https://cdn.shopify.com/s/files/1/0018/4650/9667/t/224/assets/review_bg_1000x@2x.progressive.jpg?v=15769678129892572889'

	const discountMethods = useDiscountMethods()

	const init = ()=> {
		discountMethods
			.getReferralDiscount()
			.then((discount)=>{
				setLoading(true)
				if(discount){
					setDiscountCode(discount)
					setLoading(false)
					setPageloading(false)
				}
			})
	}
	
	const getReferralLinkFromDiscount = ()=>{
		if(discountCode){
			return discountMethods.getReferralLinkFromDiscount(discountCode)
		}
		return ''
	}

	return {
		fields: {
			pageLoading,
			loading,
			referralCode,
			referralBannerImage: REFERRAL_BANNER_IMAGE
		},
		actions: {
			init,
			getReferralLinkFromDiscount
		}
	}
}

export default useDashboardReferralFormViewController
