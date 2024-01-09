import { RenderSuccessToast } from 'components/Toast'
import React from 'react'

import './styles.scss'

export interface DiscountBannerProps{
	bannerText: string
	codename: string
}

const DiscountBanner:React.FC<DiscountBannerProps> = ({
	bannerText,
	codename
	
})=>{
	const handleClick = ()=>{
		RenderSuccessToast(`Code ${codename} copied to clipboard`)
		navigator.clipboard.writeText(codename)
	}
	return (
		<div className="DiscountBanner" onClick={handleClick}>
			{bannerText}
		</div>
	)
}

export default DiscountBanner
