import React, { useState } from 'react'
import PlusOutlined from '@ant-design/icons/lib/icons/PlusOutlined'
import cx from 'classnames'

import { ChildrenID, ChildrenType } from 'api/ChildrenAPI/types'
import { Product } from 'api/ProductsAPI/types'
import { cloneDeep } from 'lodash'
import { Hx, TinyP } from 'components/Typography'
import SmoothBoyCard from 'components/SmoothBoyCard'
import { titleCase } from 'src/utils/utils'
import TinyModal from 'src/shells/TinyModal'
import { Button } from 'antd'
import RenderModal from './RenderModal'
import ChecklistQuestion from 'components/ChecklistQuestion'
import RenderChildrenWithAddonTags from './RenderAddonsWithChildTags'
import { CheckboxValueType } from 'antd/lib/checkbox/Group'
import RenderAddOnVariants from './RenderAddonVariants'

export interface RenderAddonsProps{
	existingAddons: Record<ChildrenID, Set<string>>
	setExistingAddons: (addonsRecords: Record<ChildrenID, Set<string>>) => void
	addons: Array<Product>
	customerChildren: Array<ChildrenType>
	className?: string
}

const RenderAddons:React.FC<RenderAddonsProps> = ({
	addons,
	existingAddons,
	setExistingAddons,
	customerChildren,
	className,
})=>{
	const customerChildrenChoices = (children:Array<ChildrenType>) =>{
		return children.map(({firstName,id})=>{
			return ({value: id, label: `Add to ${firstName}'s meal plan`})
		})
	}
	const getChildrenWithAddon = (addonId:string, existingAddons:Record<string, Set<string>>)=>{
		return Object.entries(existingAddons)
			.filter(([,addonIds])=> addonIds.has(addonId))
			.map(([childId])=> childId)
	}	
	const onSubmit = (addonId:string, setShouldRenderModal: (show:boolean)=> void) => (childIds: Array<CheckboxValueType>)=>{
		const addon = addons.find((addon)=> (
			addon.variants.find((variant)=> variant.id == addonId
			)
		))
		if(!addon) return // add-on should always exists, but just in case :)

		const addonCandidates = new Set(childIds)
		const _existingAddons = cloneDeep(existingAddons)

		Object.entries(_existingAddons).forEach(([childId, currentAddonIds])=>{
			// if child doesn't have add-on and should have, add it
			if(!currentAddonIds.has(addonId) && addonCandidates.has(childId)){
				currentAddonIds.add(addonId)
			}
			// else if the contrapositive is true, remove it
			else if(currentAddonIds.has(addonId) && !addonCandidates.has(childId)){
				currentAddonIds.delete(addonId)
			}
			else{
				// child has add-on, so we do nothing.
			}
		})

		setExistingAddons(_existingAddons)
		setShouldRenderModal(false)
	}

	if(!addons || !addons.length){
		return (
			<TinyP className={`
				text-center
				color-deep-ocean
				weight-300
				font-24
				weight-800
			`}>
				There&apos;s no add-ons available at this time,
				please click submit to continue to checkout
			</TinyP>
		)
	}

	return (
		<>
			{addons && (
				addons.map((addon)=>{
					return (
						<TinyRecipeCard 
							key={`recipe-card-${addon.id}`}
							addon={addon}
							className={className}
							customerChildrenChoices={customerChildrenChoices}
							getChildrenWithAddon={getChildrenWithAddon}
							existingAddons={existingAddons}
							customerChildren={customerChildren}
							onSubmit={onSubmit}
						/>
					)
				})
			)
			}
		</>
	)
}


export default RenderAddons


interface TinyRecipeCardProps{
	addon: Product
	className?:string
	existingAddons: Record<ChildrenID, Set<string>>
	customerChildrenChoices: (children:Array<ChildrenType>) => Array<{value: string, label: string}>
	getChildrenWithAddon: (addonId:string, existingAddons:Record<string, Set<string>>) => Array<string>
	customerChildren: Array<ChildrenType>
	onSubmit:(addonId:string, setShouldRenderModal: (show:boolean)=> void) => (childIds: Array<CheckboxValueType>) => void
}
const TinyRecipeCard:React.FC<TinyRecipeCardProps> = ({
	addon:{
		title,
		description='',
		imageUrl,
		price,
		ingredients,
		nutritionImageUrl,
		variants,
		showVariants
	},
	className,
	customerChildrenChoices,
	getChildrenWithAddon,
	customerChildren,
	existingAddons,
	onSubmit
})=>{
	const classes = cx('TinyRecipeCard', {
		[`${className}`]: className
	})

	const _ingredients = (() => {
		return ingredients.map(({name}) => name)
	})()

	const [shouldRenderModal, setShouldRenderModal] = useState<boolean>(false)
	const onOpenModal = ()=> setShouldRenderModal(true)
	const [currentVariant, setCurrentVariant] = useState(variants[0]) 

	const [isModalVisible, setIsModalVisible] = useState<boolean>(false) 
	const variantsWithTitles = variants.filter((variant)=> variant.title)
	const defaultChecked = getChildrenWithAddon(currentVariant.id, existingAddons)

	return (
		<div className={classes}>
			<SmoothBoyCard
				imageURL={imageUrl}
				imageALT={title}
				bodyClasses={`
				typography
				text-center
			`}
			>
				<Hx
					tag="h5"
					className={`
					font-16
					color-deep-ocean
					weight-600
					font-supria-sans
				`}
					marginBottom={1}
				>
					{titleCase(title)}
				</Hx>
				<Hx className='test'>

				</Hx>
				{description && (
					<TinyP className=' text-center color-deep-ocean weight-300 font-12 weight-800 max-width-360 margin-x-auto'>
						{description}
					</TinyP>
				)}
				{
					showVariants && variantsWithTitles.length > 1 && (
						<RenderAddOnVariants 
							variants={variantsWithTitles}
							setVariant={setCurrentVariant}
						/>
					)
				}
				<p className="AddonsForm__card-text">
					{ingredients.map(({name}, i)=>{
						const delimiter = i+1 === ingredients.length ? '' : ' • '
						return  `${titleCase(name)}${delimiter}`
					})}
				</p>
				{
					nutritionImageUrl && (
						<p className='TinyRecipeCard__nutrition-facts'
							onClick={() => setIsModalVisible(true)}
						>
					Nutrition Facts
						</p>
					)
				}

				{(ingredients.length > 0 || nutritionImageUrl) && (
					<TinyModal
						isModalVisible={isModalVisible}
						closable={true}
						onCancel={() => setIsModalVisible(false)}
					>
						{nutritionImageUrl && (
							<img src={nutritionImageUrl} />
						)}
					</TinyModal>
				)}
				<RenderChildrenWithAddonTags 
					customersChildren={customerChildren}
					existingAddons={existingAddons}
					currentVariant={currentVariant.id}
				/>
				<div
					onClick={onOpenModal}
					className={`
							cursor-pointer
							typography
							font-supria-sans
							flex
							sm-flex-direction-reverse
							justify-center
							align-center
							margin-x-auto
						`}
				>
					<Button 
						shape="circle"
						type="primary">
						<PlusOutlined />
					</Button>
					<span
						style={{marginLeft: 8}}
						className={`
						typography
						color-deep-ocean
					`}
					>
					ADD/REMOVE FROM PLAN(S) • {currentVariant && (`$${currentVariant.price}`)}
					</span>
				</div>
			</SmoothBoyCard>
			<RenderModal
				title={`Choose plans with ${titleCase(title)}`}
				isModalVisible={shouldRenderModal}
			>
				<ChecklistQuestion
					// force checklist question to rerender
					key={`${currentVariant.id}`}
					choices={customerChildrenChoices(customerChildren)}
					onSubmit={onSubmit(currentVariant.id, setShouldRenderModal)}
					onBack={()=> setShouldRenderModal(false)}
					onBackText="Cancel"
					showCheckAll
					checkAllText={`Add ${titleCase(title)} to all children`}
					defaultChecked={defaultChecked}
				/>
			</RenderModal>
		</div>
	)
}
