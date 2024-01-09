import React from 'react'
import { Button, Col, Row } from 'antd'
import { GridLoader } from 'react-spinners'

import { ChildrenID } from 'api/ChildrenAPI/types'
import { Product } from 'api/ProductsAPI/types'
import { Hx, TinyP } from 'components/Typography'
import { ButtonContainer } from 'src/shells/FormWrapper'
import { CartSliceState } from 'store/cartSlice'
import { SubscriptionSliceState } from 'store/subscriptionSlice'
import RenderAddons from './RenderAddons'

interface RenderAddonsFormProps{
	subscription: SubscriptionSliceState,
	carts: CartSliceState,
	addons: Array<Product>,
	existingAddons:Record<ChildrenID,Set<string>>
	setExistingAddons: (addons: Record<ChildrenID,Set<string>>) => void
	onSubmit: ()=> void
	onBack?: ()=> void
	title?: string
	subtitle?: string
}

const RenderAddonsForm:React.FC<RenderAddonsFormProps> = ({
	subscription,
	carts,
	existingAddons,
	setExistingAddons,
	addons,
	onSubmit,
	onBack,
	title,
	subtitle,
})=>{
	return (
		<>
			<Row className="AddonsForm">
				<Col 
					className={`
				text-center
			`} 
					span={22}
					offset={1}
				>
					{title && (
						<Hx
							tag="h5"
							className={`
								font-36
								color-deep-ocean
								text-center
							`}
							lineHeight={10}
							marginBottom={6}	
						>
							{title}
						</Hx>
					)}
					{subtitle && (
						<TinyP
							className={`
								font-16
								color-deep-ocean
								weight-300
								text-center
							`}
							lineHeight={5}
							marginBottom={8}
						>
							{subtitle}
						</TinyP>
					)}
				</Col>
				<Col span={22} offset={1}>
					<RenderAddons
						existingAddons={existingAddons} 
						setExistingAddons={setExistingAddons}
						customerChildren={subscription.children}
						addons={addons} />
				</Col>
				<Col span={22} offset={1}>
					<ButtonContainer unstickyOnMobile>
						<Button type="primary" onClick={onSubmit}>
							Next
						</Button>
						{onBack && (
							<Button type="default" onClick={()=> onBack()}>
							Back
							</Button>
						)}
					</ButtonContainer>
					{ carts.APIStatus === 'loading' && (
						<div className={`
						margin-x-auto
						width-fit-content
					`}>
							<GridLoader color='#204041' size={20} margin={4}/>
						</div>
					)}
				</Col>
			</Row>
		</>
	)
}


export default RenderAddonsForm
