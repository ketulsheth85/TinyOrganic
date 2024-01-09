import React, { useMemo, useState } from 'react'
import {PlusOutlined, MinusOutlined} from '@ant-design/icons'
import {Button} from 'antd'
import {useSelector} from 'react-redux'
import cx from 'classnames'

import { LineItemType } from 'api/CartAPI/types'
import { TinyP } from 'components/Typography'
import TinyModal from 'src/shells/TinyModal' 
import { Product } from 'api/ProductsAPI/types'
import { FulfillmentStatus } from 'api/OrderAPI/types'
import TinyTag from 'components/TinyTags'
import {RootState} from 'store/store'

import './styles.scss'

export type RecipeCardTagInfo = {
	title: string
	type: FulfillmentStatus // only for colors, not representative of status of item
	tooltipText?: string
}

type PartialProduct = Pick<Product, 'title' | 'imageUrl' | 'ingredients' | 'nutritionImageUrl' | 'featuredIngredients'>
interface RecipeCardProps extends PartialProduct{
	className?: string
	onEdit?: (action:RecipeCardActions) => void
	cartLineItem?: Partial<LineItemType>
	readonly?: boolean
	recipeTagInfo?: RecipeCardTagInfo
	children?: React.ReactNode
}

export type RecipeCardActions = 'increment' | 'decrement'

const RecipeCard:React.FC<RecipeCardProps> = ({
	className,
	title,
	imageUrl,
	ingredients,
	featuredIngredients,
	cartLineItem,
	onEdit,
	readonly,
	nutritionImageUrl,
	recipeTagInfo,
	children
})=>{
	const classes = cx('TinyRecipeCard',{
		[`${className}`]: className
	})

	const _ingredients = (()=>{
		return ingredients.map(({name})=> name)
	})()
	const [isModalVisible, setIsModalVisible] = useState<boolean>(false)
	
	return (
		<div className={classes}>
			{recipeTagInfo && (
				<TinyTag 
					className='position-absolute cursor-pointer top-0 right-0 margin-right-0'
					tooltipText={recipeTagInfo.tooltipText} 
					type={recipeTagInfo.type}
				>
					{recipeTagInfo.title}
				</TinyTag>
			)}
			<div className="TinyRecipeCard__inner">
				<div className="TinyRecipeCard__img">
					<img src={imageUrl} alt={title} />
				</div>
				<div className="TinyRecipeCard__body">
					<div className="TinyRecipeCard__content">
						<h3 className="TinyRecipeCard__header">
							{title}
						</h3>
						{/* {
							_ingredients.length > 0 && (
								<p className="TinyRecipeCard__text">
									{_ingredients.slice(0, Math.min(3,_ingredients.length)).join(', ')}
								</p>
							)
						} */}
						{featuredIngredients && (
							<p className="TinyRecipeCard__text">
								{featuredIngredients}
							</p>
						)}
						{children}
						{
							nutritionImageUrl && (
								<p className="TinyRecipeCard__nutrition-facts" 
									onClick={() => setIsModalVisible(true)}
								>
								Nutrition Facts
								</p>
							)
						}
						<RenderButton 
							readonly={readonly}
							onEdit={onEdit}
							lineItem={cartLineItem} 
						/>
					</div>
				</div>
			</div>
			{(ingredients.length > 0 || nutritionImageUrl) && (
				<TinyModal
					isModalVisible={isModalVisible}
					closable={true}
					onCancel={()=> setIsModalVisible(false)}
				>	
					{nutritionImageUrl && (
						<img src={nutritionImageUrl} />
					)}
				</TinyModal> 
			)}
		</div>
	)
}

export default RecipeCard

interface RenderButtonProps{
	readonly?: boolean
	lineItem?: Partial<LineItemType>
	onEdit?: (action:RecipeCardActions) => void
}
const RenderButton:React.FC<RenderButtonProps> = ({readonly, lineItem, onEdit})=>{
	const store = useSelector((state:RootState)=> state.subscription)

	if(readonly){
		return (
			<>
				{
					lineItem && lineItem?.quantity && (
						<Button style={{flexShrink: 0}} shape="circle" type="primary">
							{lineItem.quantity}
						</Button>
					)
				}
			</>
		)
	}

	if(!onEdit){
		return (
			<> </>
		)
	}
	if(!lineItem || lineItem.quantity === 0){
		return (
			<Button style={{flexShrink: 0}} shape="circle" type="primary" onClick={()=> onEdit('increment')}>
				<PlusOutlined />
			</Button>
		)
	}

	const onEditIncrement = () => {
		const attentiveAnalytics = (window as any).attentive
		if(attentiveAnalytics) {
			(window as any).attentive.analytics.productView({
				items: [
					{
						productId: lineItem.product?.id,
						productVariantId: lineItem.productVariant?.skuId,
						name: lineItem.product?.title,
						category: 'food',
						price: {
							value: lineItem.productVariant?.price,
							currency: 'USD',
						},
						quantity: lineItem.quantity,
					},
				],
				user: {
					phone: store.phoneNumber,
					email: store.email,
				}
			})
		}

		onEdit('increment')
	}
	return (
		<div className="TinyRecipeCard__btn-container">
			<Button shape="circle" type="primary" onClick={()=> onEdit('decrement')}><MinusOutlined/></Button>
			<div>{lineItem.quantity}</div>
			<Button shape="circle" type="primary" onClick={()=> onEditIncrement()}><PlusOutlined /></Button>
		</div>
	)
}

interface RecipePriceBreakDownProps{
	price: number,
	quantity?: number
}
export const RecipePriceBreakDown:React.FC<RecipePriceBreakDownProps> = ({price, quantity=1})=>{
	const total = parseFloat((price * quantity).toFixed(2))
	
	return (
		<div className="RecipePriceBreakDown flex align-baseline">
			<TinyP 
				className='font-16 weight-600 color-deep-ocean'
				marginBottom={1}
			>
				${total}
			</TinyP>
			{quantity > 1 && (
				<TinyP 
					className='font-12 padding-left-4 color-deep-ocean'
					marginBottom={1}
				>
					@ ${price} each
				</TinyP>
			)}
		</div>
	)
}
