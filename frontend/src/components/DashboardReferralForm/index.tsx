import React, { useEffect } from 'react'

import { SplashPage } from 'components/OnboardingSplashPage'
import { RenderPromotionCard } from 'pages/PostPurchasePage'
import { RenderErrorPage } from 'src/shells/ErrorBoundary'
import useDashboardReferralFormViewController from './vc'

import './styles.scss'


const DashboardReferralForm:React.FC = ()=>{
	const {
		fields:{
			pageLoading,
			referralCode,
			referralBannerImage
		},
		actions
	} = useDashboardReferralFormViewController()

	useEffect(()=>{
		actions.init()
	}, [])


	if(pageLoading){
		return (
			<SplashPage />
		)
	}

	if(!referralCode){
		return (
			<RenderErrorPage 
				message="We've had an issue loading your referral code, please try again later"
			/>
		)
	}

	return (
		<div className='DashboardReferralForm'>
			<RenderPromotionCard
				referralLink={actions.getReferralLinkFromDiscount()} 
				codename={referralCode} 
				image={referralBannerImage}
			/>
		</div>
	)
}

export default DashboardReferralForm
