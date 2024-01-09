import React, { useEffect } from 'react'


import RenderAddonsForm from 'components/AddonsForm/components/RenderAddonsForm'
import { SubscriptionSliceState } from 'store/subscriptionSlice'
import { CartSliceState } from 'store/cartSlice'
import AddonsFormViewController from 'components/AddonsForm/vc'

import './styles.scss'

interface RenderAddonsSectionProps{
	title?: string
	subtitle?: string
	subscription: SubscriptionSliceState
	carts: CartSliceState
	onBack: ()=> void
	onSubmit: ()=> void
}

const RenderAddonsSection:React.FC<RenderAddonsSectionProps> = ({
	title,
	subtitle,
	subscription,
	carts,
	onBack,
	onSubmit
})=>{

	const {
		fields: {
			addons,
			existingAddons,
		},
		actions
	} = AddonsFormViewController(subscription, carts, onSubmit)

	useEffect(()=>{
		actions.init()
	}, [])

	return (
		<RenderAddonsForm 
			title={title}
			subtitle={subtitle}
			carts={carts}
			subscription={subscription}
			addons={addons}
			existingAddons={existingAddons}
			setExistingAddons={actions.setExistingAddons}
			onBack={onBack}
			onSubmit={actions.onSubmit}
		/>
	)
}


export default RenderAddonsSection
