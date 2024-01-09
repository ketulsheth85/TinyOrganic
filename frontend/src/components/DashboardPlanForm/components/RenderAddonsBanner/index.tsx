import React from 'react'
import { Button } from 'antd'

import SmoothBoyCard from 'components/SmoothBoyCard'
import { Hx, TinyP } from 'components/Typography'

import './styles.scss'
import { useHistory } from 'react-router-dom'

interface RenderAddonsSectionProps{
	title?: string
	subtitle?: string
	imageUrl?: string
}

const RenderAddonsSection:React.FC<RenderAddonsSectionProps> = ({
	title,
	subtitle,
	imageUrl,
})=>{

	const DEFAULT_IMAGE_URL = 'https://cdn.shopify.com/s/files/1/0018/4650/9667/files/add_on_banner_2.jpg'
	const history = useHistory()

	const onBrowseAddons = ()=>{
		history.push('/dashboard/add-ons')
	}

	if(process.env.EDIT_ADD_ONS_IN_DASHBOARD){
		return (
			<div className='RenderAddonsSection'>
				<SmoothBoyCard
					imageURL={imageUrl || DEFAULT_IMAGE_URL}
				>
					<Hx 
						className={`
							font-36
							color-deep-ocean
							weight-600
							text-center
						`}
						marginBottom={4}
					>
						Want more Tiny?
					</Hx>
					<TinyP
						className={`
							font-16
							color-deep-ocean
							weight-300
							text-center
						`}
						lineHeight={6}
						marginBottom={3}
					>
						From larger portions of our best sellers, to a Tiny themed bib for your little one
						— add something extra to your box!
					</TinyP>
					<div className='typography text-center'>
						<Button 
							onClick={onBrowseAddons}
							className='margin-x-auto'
							type="primary"
							size='large'
							shape='round'
						>
						Manage Add-Ons
						</Button>
					</div>
				</SmoothBoyCard>
			</div>
		)
	}
	return (
		<div></div>
	)
}


export default RenderAddonsSection
