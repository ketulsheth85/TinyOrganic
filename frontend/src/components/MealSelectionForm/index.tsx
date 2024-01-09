import React, {Fragment, useEffect, useState} from 'react'
import { toast } from 'react-toastify'
import { Button, Form, Select } from 'antd'
import { get } from 'lodash'
import { isRejectedWithValue } from '@reduxjs/toolkit'
import {useDispatch, useSelector} from 'react-redux'

import { MultipageFormComponentProps } from 'src/shells/MultiPageForm'
import {getChildrenCarts, updateCartLineItems} from 'store/cartSlice'
import {AppDispatch, RootState} from 'store/store'
import {ChildrenType} from 'src/api/ChildrenAPI/types'
import useProductMethods from 'src/hooks/useProductMethods'
import { Product, RecommendedProduct } from 'api/ProductsAPI/types'
import { SplashPage } from 'components/OnboardingSplashPage'
import FormWrapper, { ButtonContainer } from 'src/shells/FormWrapper'
import RecipeCard, { RecipeCardActions, RecipeCardTagInfo } from 'components/RecipeCard'
import { CartType, LineItemType } from 'api/CartAPI/types'
import { deepClone, segmentAnalitycs } from 'src/utils/utils'
import { CreateCustomerSubscriptionPayload, CustomerSubscription } from 'api/SubscriptionAPI/types'
import FloatingCart from 'src/components/FloatingCart'
import { APIstatus } from 'store/types'
import BundleSelectionCard from 'components/BundleSelectionCard'
import { CustomerID } from 'api/CustomerAPI/types'
import { Hx, TinyP } from 'components/Typography'
import { CheckMarkFilled } from 'components/svg'
import { RenderErrorPage } from 'src/shells/ErrorBoundary'
import analyticsClient from 'src/libs/analytics'
import { Ingredient } from 'api/IngredientAPI/types'
import { FulfillmentStatus } from 'api/OrderAPI/types'
import MealSelectionSection from './components/MealSelectionSection'

import './styles.scss'

export interface ChildMealSelectionFormProps {
	title?: string
	backText?: string
	submitText?: string
	apiStatus: APIstatus
	childCart: CartType
	customer: CustomerID
	allergies?: Array<Ingredient>
	childSubscription: CustomerSubscription
	updateBundleInfo?: (payload: CreateCustomerSubscriptionPayload) => Promise<any>
	currentChild: ChildrenType
	onSubmit: (cart: CartType) => void
	onBack?: (shouldLoop?: boolean) => void
	analyticsInfo: {
		first_name: string,
		last_name: string,
		email: string
	}
	onIncrementCallback?: (product?: any) => void
	onDecrementCallback?: (product?: any) => void
}

export const ChildMealSelectionForm:React.FC<ChildMealSelectionFormProps> = ({
	title,
	backText,
	submitText,
	customer,
	currentChild,
	childCart,
	childSubscription,
	updateBundleInfo,
	apiStatus,
	analyticsInfo,
	allergies = [],
	onBack,
	onSubmit,
	onIncrementCallback,
	onDecrementCallback
})=>{

	const getItemCount = (cart: CartType)=>(
		cart.lineItems
			.filter((item)=>{
				const product = item.product as Product
				return product.productType === 'recipe'
			})
			.reduce((acc, {quantity})=>(
				acc + (quantity || 0)
			), 0)
	)

	const getProductMap = (products:Array<Product>) =>{
		const map:Record<string, Product> = {}
		products.forEach((product)=>{
			map[product.id] = product
		})
		return map
	}

	const {
		init,
		getProductsForChild
	} = useProductMethods()
	const [tinyBeginningsProducts, setTinyBeginningsProducts] = useState<Array<Product>>([]) 
	const [recommendedProducts, setRecommendedProducts] = useState<Array<Product>>([])
	const [products, setProducts] = useState<Array<Product>>([])
	const [allProducts, setAllProducts] = useState<Array<Product>>([])
	const [cart, setCart] = useState<CartType>(childCart)
	const [itemCount, setItemCount] = useState<number>(getItemCount(cart))

	const [numberOfServings, setNumberOfServings] = 
	useState<number>(get(childSubscription,'numberOfServings', 24) as number)
	const [frequency, setFrequency] = 
	useState<number>(get(childSubscription, 'frequency', 2) as number)

	useEffect(()=>{
		// if this is false, then we are most likely embedding this form in another page
		if(!updateBundleInfo){
			analyticsClient.pageView('Onboarding ', 'Meal plan Selection', {
				...analyticsInfo,
				child: currentChild.firstName
			})
		}
	},[])

	useEffect(()=>{
		setCart(childCart)
		setItemCount(getItemCount(childCart))

	}, [childCart])


	const incrementLineItem = (_cart: CartType, id:string) =>{
		let idx = -1
		const cartItem = _cart.lineItems.find(({product})=>{
			idx++
			return product && product.id === id
		})
		if(cartItem){
			const lineItem = _cart.lineItems[idx] as LineItemType
			lineItem.quantity += 1
		}
		else{
			const product = allProducts.find((p)=>{
				return p.id === id
			})
			_cart.lineItems.push({
				product,
				quantity: 1
			})
			if(onIncrementCallback) onIncrementCallback(product)
		}
		setItemCount((count)=>count + 1)
		return _cart
	}

	const decrementLineItem = (_cart: typeof cart, id:string) =>{
		let idx = -1
		const cartItem = _cart.lineItems.find(({product})=>{
			idx++
			return product && product.id === id
		})
		if(cartItem && cartItem.quantity as number <= 1){
			const lineItem = _cart.lineItems[idx] as LineItemType
			lineItem.quantity = 0
			if(onDecrementCallback) onDecrementCallback(lineItem)
		}
		else if(cartItem){
			const lineItem = _cart.lineItems[idx] as LineItemType
			lineItem.quantity -= 1
			if(onDecrementCallback) onDecrementCallback(lineItem)
		}
		else{
			/**
			 * This runs if we try to delete an item that's not
			 * in the cart, shouldn't happen but just in case ;)
			 */
		}
		setItemCount((count)=> count - 1)
		return _cart
	}

	const editLineItem = (id:string) => (action:RecipeCardActions) =>{
		let _cart:CartType = deepClone(cart)
		
		if(itemCount >= numberOfServings &&
			action === 'increment'	
		){
			toast.info('Your cart is full, try removing an item(s) before adding this one')
			return
		}
		
		if(action === 'increment'){
			_cart = incrementLineItem(_cart, id)
		}
		else if(action === 'decrement'){
			_cart = decrementLineItem(_cart, id)
		}
		setCart(_cart)
	}

	const extractProducts = (recommendedProducts: Array<RecommendedProduct>) =>{
		return recommendedProducts.map(({product})=> product)
	}

	useEffect(()=>{
		getProductsForChild(currentChild.id)
			.then((data)=>{
				const _tinyBeginningsProducts = extractProducts(data.tinyBeginnings)
				const recommendations = extractProducts(data.recommendations)
				const remainingProducts = extractProducts(data.remainingProducts)

				setTinyBeginningsProducts(_tinyBeginningsProducts)
				setRecommendedProducts(recommendations)
				setProducts(remainingProducts)
				setAllProducts(
					recommendations
						.concat(remainingProducts)
						.concat(_tinyBeginningsProducts)
				)
			})
	}, [numberOfServings])

	const _onSubmit = ()=>{
		if(itemCount > numberOfServings){
			toast.error(`You have ${itemCount} meals in your cart, but your bundle
			meal plan has a max of ${numberOfServings}. Either change your bundle
			or remove ${itemCount - numberOfServings} meals to continue
			`)
			return
		}
		else if(itemCount < numberOfServings){
			return
		}
		const productMap = getProductMap(allProducts)
		const _cart = deepClone(cart) as CartType
		_cart.lineItems.forEach((item)=>{
			const product = item.product
			if(product && product.productType === 'recipe'){
				item.product = productMap[item.product?.id as string]
			}
		})

		const attentiveAnalytics = (window as any).attentive && (window as any).attentive.analytics
		if(attentiveAnalytics) {
			const cartLineItems: Array<any> = []
			_cart.lineItems.forEach((item) => {
				const product = item.product
				cartLineItems.push({
					productId: product?.id,
					productVariantId: item.id,
					name: product?.title,
					productImage: product?.imageUrl,
					category: product?.productType,
					price: {value: item.productVariant?.price, currency: 'USD' },
					quantity: item.quantity
				})
			})
			attentiveAnalytics.addToCart({
				items: cartLineItems,
				cart: { cartId: _cart.cartId, },
				user: { email: analyticsInfo.email },
			})
		}
		if(updateBundleInfo){
			updateBundleInfo({
				customer,
				customerChild: currentChild.id,
				frequency,
				numberOfServings
			})
				.then((action:any)=>{
					if(isRejectedWithValue(action)) return
					onSubmit(_cart)
				})
		}
		else{
			/**
			 * We call window object directly as we've had issues
			 * with other scripts in the past when adding adapters
			 */
			(window as any).liQ = (window as any).liQ || [];
			(window as any).liQ.push({
				'event': 'addToCart',
				'email': analyticsInfo.email
			})
			onSubmit(_cart)
		}
	}

	if(!init){
		return (
			<SplashPage />
		)
	}

	const allergyNameSet = new Set(allergies.map(({name})=>name))

	const createAllergyTagInfoFromRecipe = (product:Product):RecipeCardTagInfo | undefined =>{

		const name = currentChild.firstName ? `${currentChild.firstName}'s` : 'Your child\'s'
		const allergyList = product.ingredients.
			filter((ingredient)=> {
				return allergyNameSet.has(ingredient.name)
			})
			.map((ingredient)=> ingredient.name)
			.join(', ')

		if(allergyList.length === 0) return

		return {
			title: 'Has Allergies',
			type: FulfillmentStatus.cancelled,
			tooltipText: `${name} is allergic to ${allergyList}.`
		}
	}

	const formTitle = title || `${currentChild.firstName}'s Meal Plan`
	const features = [
		'Full of nutrients for growing children',
		'Full of diverse flavors and ingredients',
		'Free of the eight big allergens',
		'Perfect for little ones starting solids'
	]

	return (
		<div className="ChildMealSelectionForm">
			<RenderBanner 
				title={formTitle}
				features={features}
			/>
			<FormWrapper
				className="OnboardingPageOverrides"
			>
				<>
					<div className="ChildMealSelectionForm__body">
						{updateBundleInfo && (
							<RenderBundleSelection 
								numberOfServings={numberOfServings}
								setNumberOfServings={setNumberOfServings}
								frequency={frequency}
								setFrequency={setFrequency}
							/>
						)}
						<MealSelectionSection 
							title={`Picked just for ${currentChild.firstName}:`}
							headerClasses='color-pink-dark'
							products={recommendedProducts}
							onEditLineItem={editLineItem}
							recipeTagInfoFunc={createAllergyTagInfoFromRecipe}
							numberOfServings={numberOfServings}
							cart={cart}
						/>
						<MealSelectionSection 
							title='All Tiny Meals'
							headerClasses='color-deep-ocean'
							products={products}
							onEditLineItem={editLineItem}
							recipeTagInfoFunc={createAllergyTagInfoFromRecipe}
							numberOfServings={numberOfServings}
							cart={cart}
						/>
						<MealSelectionSection 
							title='Tiny Beginnings'
							subtitle='Nourishing organic finger foods for little ones 4 months +
							Baby-led weaning compatible, these meals offer bigger, bite-size pieces for your littlest eater.'
							headerClasses='color-pink-dark'
							products={tinyBeginningsProducts}
							onEditLineItem={editLineItem}
							recipeTagInfoFunc={createAllergyTagInfoFromRecipe}
							numberOfServings={numberOfServings}
							cart={cart}
						/>
					</div>
					<ButtonContainer unstickyOnMobile>
						<>
							<RenderRemark 
								itemCount={itemCount}
								numberOfServings={numberOfServings}
							/>
							<Button
								className="margin-bottom-20"
								loading={apiStatus === 'loading'}
								type="primary"
								size="large"
								onClick={_onSubmit}
								disabled={itemCount < numberOfServings}
							>
								{submitText || 'Pick your meals'}
							</Button>
							{
								onBack && (
									<Button
										type="default"
										size="large"
										htmlType="button"
										onClick={()=> onBack()}
									>
										{backText || 'Back'}
									</Button>
								)
							}
						</>
					</ButtonContainer>
				</>
			</FormWrapper>
			<FloatingCart 
				title={`${currentChild.firstName}'s Meal Plan`}
				count={itemCount} 
				limit={numberOfServings}
				onSubmit={_onSubmit}
				disabled={itemCount < numberOfServings}
				loading={apiStatus === 'loading'}
			>
				{
					allProducts.map((product)=>{
						const lineItem = cart.lineItems.find((item)=>{
							return product && item.product?.id === product.id
						})
						if(!lineItem || !lineItem.quantity) return <></>
						return (
							<div className="ChildMealSelectionForm__meal" key={product.id}>
								<RecipeCard									
									title={product.title}
									imageUrl={product.imageUrl}
									ingredients={product.ingredients}
									onEdit={editLineItem(product.id)}
									cartLineItem={lineItem}
									nutritionImageUrl={product.nutritionImageUrl}
									recipeTagInfo={createAllergyTagInfoFromRecipe(product)}
								/>
							</div>
						)
					})
				}
			</FloatingCart>
		</div>
	)
}

interface RenderBannerProps{
	title: string
	features?: Array<string>
}
const RenderBanner:React.FC<RenderBannerProps> = ({title, features})=>{
	return (
		<div className={`
			ChildMealSelectionForm__banner
			max-width-900
			-margin-top-20
			padding-x-32
			padding-y-40
			background-mint
			typography
			text-center
		`}>
			<Hx 
				className={`
					color-deep-ocean
					font-24
					font-36-md
				`}
				marginBottom={4}
			>
				{title}
			</Hx>
			<TinyP
				className={`
					color-deep-ocean
					font-16
				`}
				marginBottom={3}
			>
				We’ve picked meals for your little one that are:
			</TinyP>
			<div className="width-fit-content margin-x-auto">
				{features && features.map((text)=>(
					<TinyP
						key={text}
						className={`
					flex
					align-center
					color-deep-ocean
					font-16
					font-italic
					weight-600
				`}
						marginBottom={2}
					>
						<span className="margin-right-8">
							<CheckMarkFilled />
						</span>
						{text}
					</TinyP>
				))}
			</div>

		</div>
	)
}

interface RenderRemarkProps{
	itemCount: number
	numberOfServings: number
}

const RenderRemark:React.FC<RenderRemarkProps> = ({
	itemCount, 
	numberOfServings
})=>{
	if(itemCount > numberOfServings){
		return (
			<p className="ButtonContainer__remark ButtonContainer__remark--error">
				{`You have ${itemCount} meals in your cart, but your bundle
				meal plan has a max of ${numberOfServings}. Either change your bundle
				or remove ${itemCount - numberOfServings} meals to continue
				`}
			</p>
		)
	}
	return (
		<p className="ButtonContainer__remark">
			{`${itemCount}/${numberOfServings} meals chosen`}
		</p>
	)
}

const ChildrenMealSelectionFormHOC:React.FC<MultipageFormComponentProps> = ({
	shouldSeeQuestion,
	onBack,
	onSubmit,
}) => {
	const [state, setState] = useState({
		cursor: 0,
		error: '',
		shouldRender: false,
		cart: {id: '', lineItems: [{}]},
	})

	const dispatch = useDispatch<AppDispatch>()
	const {subscription, carts} = useSelector((state: RootState) => state)

	const init = async ()=>{
		const _shouldRenderQuestion = shouldSeeQuestion(`
			It looks like you haven't gotten to "Meal selection" just yet,
			please fill out the form below to continue 😊
		`)
		if(!_shouldRenderQuestion) return 

		const childrenCartsAction = 
			await dispatch(getChildrenCarts(subscription.id))
		
		if(isRejectedWithValue(childrenCartsAction)){
			setState((state)=>{
				return {
					...state,
					error: `
						We had an issue loading your bundle info, please
						reload the page
					`
				}
			})
		}
		setState((state)=>{
			return {
				...state,
				shouldRender: true
			}
		})
	}

	useEffect(() => {
		init()
	}, [])

	const _onSubmit = (cart: CartType) => {
		const lineItems = cart.lineItems
		const shouldLoop = state.cursor + 1 < subscription.children.length
		dispatch(updateCartLineItems({
			cartId: cart.cartId,
			customerId: subscription.id,
			lineItems: cart.lineItems
		}))
			.then((action) => {
				const attentiveAnalytics = (window as any).attentive
				if(attentiveAnalytics) {
					// fire off attentive mobile event
					attentiveAnalytics.analytics.addToCart({
						user: {
							phone: subscription.phoneNumber || '',
							email: subscription.email,
						},
						items: lineItems.map((lineItem) => {
							return {
								id: lineItem.id,
								productId: lineItem.product?.id,
								productVariantId: lineItem.productVariant?.skuId,
								name: lineItem.product?.title,
								quantity: lineItem.quantity,
								category: 'food',
								price: {
									value: lineItem.productVariant?.price,
									currency: 'USD',
								},
							}
						}),
						cart: {
							cartId: cart.id,
						}
					})
				}
				// fire off google event
				(window as any).gtag('event', 'add_to_cart', {
					items: lineItems.map((lineItem) => {
						return {
							id: lineItem.id,
							name: lineItem.product?.title,
							quantity: lineItem.quantity,
							price: lineItem.productVariant?.price,
						}
					})
				}) // don't remove semi-colon
				// eslint-disable-next-line no-unexpected-multiline
				if((window as any).analytics){
					(window as any).analytics.track('Add to cart', {
						email: subscription.email,
						last_name: subscription.lastName,
						first_name: subscription.firstName,
						cart: cart.cartId,
						customer_id: subscription.id,
						line_items: lineItems.map((lineItem) => {
							return {
								id: lineItem.id,
								title: lineItem.product?.title,
								quantity: lineItem.quantity,
								price: lineItem.productVariant?.price,
							}
						})
					})
				}

				if(isRejectedWithValue(action)) return 
				if (shouldLoop) {
					setState(({cursor, ...rest}) => {
						return {
							...rest,
							cursor: cursor + 1
						}
					})
				} else {
					onSubmit()
				}
			})
	}
	const _onBack = (shouldLoop?: boolean) => {
		const _shouldLoop = state.cursor > 0
		if (_shouldLoop) {
			setState(({cursor, ...rest}) => {
				return {
					...rest,
					cursor: cursor - 1
				}
			})
		} else if (onBack) {
			onBack(shouldLoop)
		}
	}

	if(state.error){
		return (
			<RenderErrorPage 
				message={state.error}
			/>
		)
	}

	if(!carts.init || !state.shouldRender){
		return (
			<SplashPage />
		)
	}

	const onIncrementCallback = (product: any) => {
		segmentAnalitycs("Product Added", {
			product_id: product?.id,
			category: product?.productType,
			name: product?.title,
			image_url: product?.imageUrl,
			sku: [
				product?.variants.map((variant: any) => {
					return {
						variantId: variant.id,
						sku: variant.skuId,
						price: variant.price
					}
				})
			]
		})
	}

	const onDecrementCallback = (product: any) => {
		segmentAnalitycs("Product Removed", {
			product_id: product?.id,
			category: product?.productType,
			name: product?.title,
			image_url: product?.imageUrl
		})
	}

	return (
		<>
			{subscription.children.map((child: ChildrenType, i: number) => {
				const {subscriptions} = subscription
				// Child is not in cart first time around for some reason
				return (
					<Fragment key={child.firstName}>
						{
							state.cursor === i && (
								<ChildMealSelectionForm
									onIncrementCallback={onIncrementCallback}
									onDecrementCallback={onDecrementCallback}
									key={child.id}
									analyticsInfo={{
										first_name: subscription.firstName,
										last_name: subscription.lastName,
										email: subscription.email
									}}
									customer={subscription.id}
									onSubmit={_onSubmit}
									currentChild={child}
									onBack={onBack && _onBack}
									childSubscription={subscriptions[child.id]}
									childCart={carts.children[child.id]}
									apiStatus={carts.APIStatus}
								/>
							)
						}
					</Fragment>
				)
			})}
		</>
	)
}

export default ChildrenMealSelectionFormHOC

interface RenderBundleSelectionProps {
	numberOfServings: number
	setNumberOfServings: (num:number)=> void
	frequency: number
	setFrequency: (num: number)=> void
}
export const RenderBundleSelection:React.FC<RenderBundleSelectionProps> = ({
	numberOfServings,
	setNumberOfServings,
	frequency,
	setFrequency
})=>{
	return (
		<FormWrapper
			className="OnboardingPageOverrides"
		>
			<div className="BundleSelectionForm__body">
				<div className="BundleSelectionForm__cards">
					<BundleSelectionCard 
						title="12"
						subheader="meals"
						text="Pay $5.49 per meal"
						active={numberOfServings === 12}
						onClick={()=> setNumberOfServings(12)}
					/>
					<BundleSelectionCard 
						featuredText="Best Value"
						title="24"
						subheader="meals"
						text="Starting at $4.66 per meal"
						active={numberOfServings === 24}
						onClick={()=> setNumberOfServings(24)}
					/>
				</div>
				<div>
					<Form.Item
						name="frequency"
						rules={[{ required: true, message: 'This field is required' }]}
						initialValue={frequency}
					>	
						<p className="BundleSelectionForm__label">every</p>
						<Select
							value={frequency as number}
							placeholder="Select Delivery frequency"
							onChange={(value:number)=>{
								setFrequency(value)
							}}
						>
							<Select.Option value={1}>1 weeks</Select.Option>
							<Select.Option value={2}>2 weeks</Select.Option>
							<Select.Option value={4}>4 weeks</Select.Option>
						</Select>
					</Form.Item>
				</div>
			</div>
		</FormWrapper>
	)
}
