import React from 'react'

import { ChildrenType } from 'api/ChildrenAPI/types'
import TinyModal from 'src/shells/TinyModal'
import { LineItemType } from 'api/CartAPI/types'
import RenderLineItems from '../RenderLineItems'
import { TinyP } from 'components/Typography'
import { Button } from 'antd'

interface RenderAllergyWarningModal{
	child: ChildrenType,
	isModalVisible: boolean
	onClose: ()=> void
	recipesWithAllergies: Array<LineItemType>
}
const RenderAllergyWarningModal:React.FC<RenderAllergyWarningModal> = ({
	child,
	isModalVisible,
	recipesWithAllergies,
	onClose
})=>{
	return (
		<TinyModal
			title={`${child.firstName} may be allergic to these recipes in their current subscription`}
			isModalVisible={isModalVisible}
		>
			<TinyP className='margin-x-20 font-16 color-black' lineHeight={7}>
				<strong>{child.firstName}&apos;s allergies:</strong> <br/>
			</TinyP>
			<TinyP className='-margin-top-20 font-16 weight-300 color-deep-ocean'>
				{(child.allergies || [])
					.map(({name})=> name)
					.join(', ')}
			</TinyP>
			<TinyP className='margin-x-20 font-16 color-black' lineHeight={7}>
				<strong>Recipes with allergies:</strong> <br/>
			</TinyP>
			<TinyP className='-margin-top-20 font-16 weight-300 color-deep-ocean' lineHeight={7}>
				You can replace these recipes for other tasty meals by heading over to &nbsp;
				&quot;meal selection&quot; under {`"${child.firstName}'s`} Subscription.&quot;
			</TinyP>
			<RenderLineItems 
				fullWidthCells
				lineItems={recipesWithAllergies}
			/>
			<Button 
				onClick={onClose}
				className="margin-top-20" type="primary"
			>
				Close
			</Button>
		</TinyModal>
	)
}

export default RenderAllergyWarningModal
