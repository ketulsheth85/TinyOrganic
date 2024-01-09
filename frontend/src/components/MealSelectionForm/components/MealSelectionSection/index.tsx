import React from 'react'
import cx from 'classnames'
import { endsWith } from 'lodash'

import { Hx } from 'components/Typography'
import { Product } from 'api/ProductsAPI/types'
import RecipeCard, { RecipeCardActions, RecipeCardTagInfo, RecipePriceBreakDown } from 'components/RecipeCard'
import { CartType, LineItemType } from 'api/CartAPI/types'

interface MealSelectionSectionProps{
	title: string
	subtitle?: string
	products: Array<Product>
	numberOfServings: number
	onEditLineItem: (productId: string) => (action:RecipeCardActions) => void
	recipeTagInfoFunc?: (product:Product) => RecipeCardTagInfo | undefined
	cart: CartType
	headerClasses?: string
	subHeaderClasses?: string
}
const MealSelectionSection:React.FC<MealSelectionSectionProps> = ({
	title,
	subtitle,
	products,
	numberOfServings,
	onEditLineItem,
	recipeTagInfoFunc,
	cart,
	headerClasses,
	subHeaderClasses
})=>{
	const getLineItem = (product:Product)=>(
		cart.lineItems.find((item)=>{
			return product && item.product?.id === product.id
		})
	)

	const getLineItemQuantity = (lineItem?: Partial<LineItemType>)=>{
		let quantity = 1
		if(lineItem){
			if(lineItem.quantity){
				quantity = lineItem.quantity
			}
		}
		return quantity								
	}

	const _headerClasses = cx(`
	margin-top-20 
	-margin-bottom-4 
	text-center 
	font-24
	weight-600
		`,{
		[`${headerClasses}`]: !!headerClasses
	})

	const _subHeaderClasses = cx(`
	max-width-480
	text-center
	color-deep-ocean
		`,{
		[`${subHeaderClasses}`]: !!subHeaderClasses
	})

	const getPrice = (product:Product)=>{
		const twelvePackVariant = product
			.variants
			.find((variant) => endsWith(`${variant.skuId}`, '-12'))
		
		const twentyFourPackVariant = product
			.variants
			.find((variant) => endsWith(`${variant.skuId}`, '-24')) || twelvePackVariant

		let price = 0
		if(twelvePackVariant){
			if(numberOfServings === 12){
				price = twelvePackVariant.price
			}
			if(numberOfServings === 24){
				price = twentyFourPackVariant?.price || price
			}
		}
		return price
	}

	if(!products || products.length === 0){
		return (
			<></>
		)
	}

	return (
		<>
			<div className="width-100 margin-bottom-36">
				<Hx
					tag="h2"
					className={_headerClasses}
					marginBottom={0}
				>
					{title}
				</Hx>
			</div>
			{subtitle && (
				<div className={`
					width-100 
					-margin-top-20
					margin-bottom-36
					flex
					justify-center	
				`}
				>
					<Hx
						tag="h4"
						className={_subHeaderClasses}
						marginBottom={0}
					>
						{subtitle}
					</Hx>
				</div>
			)}
			{
				products.map((product)=>{
					const price = getPrice(product)
					const lineItem = getLineItem(product)
					
					return (
						<div className="ChildMealSelectionForm__meal" key={`${title}-${product.id}`}>
							<RecipeCard									
								title={product.title}
								imageUrl={product.imageUrl}
								ingredients={product.ingredients}
								onEdit={onEditLineItem(product.id)}
								cartLineItem={getLineItem(product)}
								featuredIngredients={product.featuredIngredients}
								nutritionImageUrl={product.nutritionImageUrl}
								{...(recipeTagInfoFunc && {
									recipeTagInfo:recipeTagInfoFunc(product)
								})}
							>
								{price && (
									<RecipePriceBreakDown 
										price={price}
										quantity={getLineItemQuantity(lineItem)}
									/>
								)}
							</RecipeCard>
						</div>
					)
				})
			}
		</>
	)
}

export default MealSelectionSection
