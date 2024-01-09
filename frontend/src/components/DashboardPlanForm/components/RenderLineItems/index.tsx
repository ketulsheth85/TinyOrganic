import React from 'react'
import { Row, Col } from 'antd'
import { get } from 'lodash'

import RecipeCard, { RecipeCardTagInfo, RecipePriceBreakDown } from 'components/RecipeCard'
import { LineItemType } from 'api/CartAPI/types'
import { Product } from 'api/ProductsAPI/types'
import { FulfillmentStatus } from 'api/OrderAPI/types'
import { Ingredient } from 'api/IngredientAPI/types'

interface RenderLineItemsProps{
	fullWidthCells?: boolean
	lineItems: Array<LineItemType>
	allergies?: Array<Ingredient>
	firstName?: string
}
const RenderLineItems:React.FC<RenderLineItemsProps> = ({
	lineItems,
	fullWidthCells,
	allergies = [],
	firstName
})=>{

	// TODO: move functions to View model

	const allergyNameSet = new Set(allergies.map(({name})=>name))

	const createAllergyTagInfoFromRecipe= (product:Product):RecipeCardTagInfo | undefined =>{

		const name = firstName ? `${firstName}'s` : 'Your child\'s'
		const allergyList = product.ingredients.
			filter((ingredient)=> allergyNameSet.has(ingredient.name))
			.map((ingredient)=> ingredient.name)
			.join(', ')

		if(allergyList.length === 0) return

		return {
			title: 'Has Allergies',
			type: FulfillmentStatus.cancelled,
			tooltipText: `${name} is allergic to ${allergyList}.`
		}
	}

	return (
		<Row gutter={16} className="margin-top-20 align-stretch">
			{
				lineItems && lineItems.map((item)=>{
					const {
						imageUrl,
						ingredients,
						nutritionImageUrl,
					} = item.product
					const getFormattedTitle = (item:LineItemType)=>{
						let formattedTitle = item.product.title
						if(item.product.showVariants){
							if(item.product.productType !== 'recipe'){
								formattedTitle += ` (${item.productVariant?.title})`
							}
						}
						return formattedTitle
					}

					const price = get(item, 'productVariant.price', 0.00)
					
					return (
						<Col
							key={item.id}	
							span={24}	
							{...(!fullWidthCells && {
								md: 12
							})}
						>
							<RecipeCard
								className="margin-x-auto"					
								title={getFormattedTitle(item)}
								imageUrl={imageUrl}
								ingredients={ingredients || []}
								cartLineItem={item}
								nutritionImageUrl={nutritionImageUrl}
								recipeTagInfo={createAllergyTagInfoFromRecipe(item.product)}
								readonly
							>
								<RecipePriceBreakDown 
									price={price}
									quantity={item.quantity}
								/>
							</RecipeCard>
						</Col>
					)
				})
			}

		</Row>
	)
}

export default RenderLineItems
