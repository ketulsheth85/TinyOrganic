import React, { useEffect, useMemo, useState } from 'react'
import { Col, Row } from 'antd'
import { useSelector } from 'react-redux'
import { capitalize } from 'lodash'

import HowDidYouHearForm from 'components/HowDidYouHearForm'
import Navigation from 'components/Navigation'
import { Hx, TinyP } from 'components/Typography' 
import SmoothBoyCard from 'components/SmoothBoyCard'
import TextInputWithButton from 'components/TextInputWithButton'
import { RenderSuccessToast } from 'components/Toast'
import analyticsClient from 'src/libs/analytics'
import { RootState } from 'store/store'
import useDiscountMethods from 'src/hooks/useDiscountMethods'
import { SplashPage } from 'components/OnboardingSplashPage'
import { Discount } from 'api/DiscountAPI/types'
import useShareASaleMethods from 'src/hooks/useShareASaleMethods'
import { 
	YOTPO_REFERRAL_LINK_BASE_URL 
} from 'src/utils/constants'

import './styles.scss'


const PostPurchasePage:React.FC = ()=>{

	const {subscription} = useSelector((state: RootState) => state)
	const [coupon, setCoupon] = useState<Discount | void>()
	const [loadingCoupon, setLoadingCoupon] = useState(true)
	const discountMethods = useDiscountMethods()
	const shareASaleMethods = useShareASaleMethods()

	useEffect(()=>{
		discountMethods
			.getReferralDiscount()
			.then((coupon)=>{
				setCoupon(coupon)
			})
			.finally(()=>{
				setLoadingCoupon(false)
			})
	}, [])

	useEffect(()=>{
		if(subscription.id){
			analyticsClient
				.pageView('Post Checkout', 'Post Purchase Page',{
					first_name: subscription.firstName,
					last_name: subscription.lastName,
					email: subscription.email
				})
		}
	},[subscription])

	const [loading, setLoading] = useState(false)

	const onSubmit = ()=>{
		setLoading(true)
		RenderSuccessToast('Thanks for the feedback, you\'ll be redirected to login page shortly :)',
			{position: 'top-center'})
		setTimeout(()=>{
			window.location.replace('/accounts/login')
		}, 3000)
	}

	const theShareASaleParams = useMemo(()=>{
		return shareASaleMethods.loadShareSaleParams()
	}, [])

	if(loadingCoupon){
		return (
			<SplashPage />
		)
	}
	

	return (
		<div className="PostPurchasePage">
			<Navigation />
			<Row className="PostPurchasePage__body">
				<Col span={24} md={12}  className="PostPurchasePage__greeting">
					<Row justify="center" align="middle">
						<Col span={22} md={18}>
							<RenderGreeting />
							{
								coupon && (
									<RenderPromotionCard 
										referralLink={discountMethods.getReferralLinkFromDiscount(coupon)}
										codename={coupon?.codename}
									/>
								)
							}
						</Col>
					</Row>
				</Col>
				<Col span={24} md={12}  className="PostPurchasePage__questionnare">
					<Row justify="center" align="middle">
						<Col span={22} md={18}>
							<HowDidYouHearForm 
								loading={loading}
								onSubmit={onSubmit}
							/>
						</Col>
					</Row>
				</Col>
			</Row>
			<img 
				src={`https://www.shareasale.com/sale.cfm${theShareASaleParams}}&merchantID=112071&transtype=sale`} 
				width="1" height="1">
			</img>
		</div>
	)
}


interface RenderPromotionCardProps{	
	image?:string
	title?: string
	subtitle?: string
	codename?: string
	referralLink?:string
}
export const RenderPromotionCard:React.FC<RenderPromotionCardProps> = ({
	title='Give $30, Get $30.',
	subtitle='Refer a friend! Your friends will get $30 off their first order, and we’ll give you $30 credit for each friend who joins the Tiny family.',
	referralLink,
	codename,
	image='/static/assets/cool-baby.png'
})=>{

	const discountDescription = referralLink ? 'referral link' : 'coupon code'
	const discountString = referralLink || codename || ''

	return (
		<SmoothBoyCard imageURL={image}>
			<Hx 
				className={`
				font-24
				color-deep-ocean
				weight-600
			`}
				marginBottom={2}
			>
				{title}
			</Hx>
			<TinyP
				className={`
				font-16
				color-deep-ocean
				weight-300
			`}
				lineHeight={6}
			>
				{subtitle}
			</TinyP>
			{
				discountString &&	<>
					<TinyP 
						className={`
						font-16
						font-italic
						color-deep-ocean
						weight-600
					`}
					>
						{`Your unique ${discountDescription}:`}
					</TinyP>
					<TextInputWithButton 
						onClickElement={()=>{
							RenderSuccessToast(`${capitalize(discountDescription)} copied to clipboard`)
							navigator.clipboard.writeText(discountString)
						}}
						value={discountString}
						readonly
						cta="COPY"
					/>
				</>
			}
		</SmoothBoyCard>
	)
}

const RenderGreeting = ()=>{
	return (
		<div>
			<TinyP
				className={`
			color-pink-dark
			font-16
			font-italic
		`}
			>
				Thank you! your order has been confirmed.
			</TinyP>
			<Hx 
				tag="h3"
				className={`
				font-36
				font-54-sm
				color-deep-ocean
		`}
			>
				Welcome to the Tiny Family
			</Hx>
			<Hx
				tag="h5"
				className={`
			font-16
			color-deep-ocean
			weight-500
		`}
				marginBottom={6}
				lineHeight={6}
			>
				We at Tiny Organics are so excited to introduce your 
				little one to their first 100 Flavors!
			</Hx>
			<TinyP
				className={`
			font-16
			color-deep-ocean
			weight-300
		`}
				marginBottom={6}
				lineHeight={6}
			>
				Orders placed by 10AM ET Monday-Friday typically
				ship within 2-7 business days. You’ll receive an email with tracking
				information once your order ships. We appreciate your patience!
			</TinyP>
		</div>
	)
}


export default PostPurchasePage
