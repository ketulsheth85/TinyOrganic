import React from 'react'
import { Tag } from 'antd'

import { ChildrenType } from 'api/ChildrenAPI/types'
import { TinyP } from 'components/Typography'

interface RenderChildrenWithAddonTagsProps{
	customersChildren: Array<ChildrenType>
	existingAddons: Record<string, Set<string>>
	currentVariant: string
}

const RenderChildrenWithAddonTags:React.FC<RenderChildrenWithAddonTagsProps> = ({
	customersChildren,
	existingAddons,
	currentVariant
}) =>{
	const childrenWithAddons = customersChildren.filter( child => (
		existingAddons[child.id] && existingAddons[child.id].has(currentVariant)
	))
	return (
		<div className="RenderChildrenWithAddonTags">
			{childrenWithAddons.length > 0 && (
				<TinyP className={`
					color-deep-ocean
					weight-300
					font-14
				`}
				marginBottom={2}
				>
					Children with this add-on: &nbsp;
				</TinyP>
			)}
			{
				childrenWithAddons.map((child)=>(
					<Tag 
						key={`${child.id}-addon-tag`}
						color='green'
					>
						{child.firstName}
					</Tag>
				))
			}
		</div>
	)
}

export default RenderChildrenWithAddonTags
