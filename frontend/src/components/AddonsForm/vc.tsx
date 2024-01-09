import { useEffect, useState } from 'react'

import { ChildrenID } from 'api/ChildrenAPI/types'
import { Product } from 'api/ProductsAPI/types'
import useProductMethods from 'src/hooks/useProductMethods'
import { SubscriptionSliceState } from 'store/subscriptionSlice'
import { CartSliceState, updateCartLineItems, initStore as initCartStore } from 'store/cartSlice'
import { CartType } from 'api/CartAPI/types'
import { dispatch } from 'store/store'
import { isRejectedWithValue } from '@reduxjs/toolkit'
import { deepClone } from 'src/utils/utils'

type AddonviewControllerFields = {
	addons: Array<Product>
	existingAddons: Record<ChildrenID,Set<string>>
	shouldRender: boolean
}

type AddonsViewControllerMethods = {
	init: ()=> Promise<Array<Product> | void>
	onSubmit: ()=> Promise<void>
	setExistingAddons: (addons: Record<ChildrenID,Set<string>>) => void
}

type AddonsViewControllerMembers = {
	fields: AddonviewControllerFields,
	actions: AddonsViewControllerMethods
}

const AddonsFormViewController = (
	subscription: SubscriptionSliceState,
	carts: CartSliceState,
	onSubmit?: (shouldLoop?:boolean) => void
):AddonsViewControllerMembers => {
	const productMethods = useProductMethods()
	const [addons, setAddons] = useState<Array<Product>>([])
	const [existingAddons, setExistingAddons] = useState<Record<ChildrenID,Set<string>>>({})
	const [shouldRender, setShouldRender] = useState(false)
	const [initialized, setInitialized] = useState<boolean>(false)
	
	const init = async ()=>{
		await productMethods
			.getProducts({
				is_active: 'true',
				product_type: 'add-on'
			})
			.then((data)=>{
				setAddons(data)
			})
		
		if(!carts.init){
			const _action = await dispatch((initCartStore(subscription.id)))
			if(isRejectedWithValue(_action)) {
				return
			}
		}
		setInitialized(true)
		return addons
	}

	const getAddonVariantsSet = (addons: Array<Product>)=>{
		if(!addons){
			return new Set()
		}
		return new Set(addons.reduce((acc:Array<any>, addon:Product)=>{
			return acc.concat(addon.variants.map((variant)=> variant.id))
		}, []))
	}


	/**
	 * Cherry picks the intersections of child add-ons and add-on
	 * variants displayed on the page. The intersection is used to
	 * show users what childs have the add-ons variants from this page.
	 * 
	 * The data structure returned maps the child ids to their
	 * corresponding add-on variant intersection
	 */
	const getAddonsFromCart = async (carts:Record<ChildrenID, CartType>) =>{
		const childrenWithAddons:Record<ChildrenID, Set<string>> = {}
		const addonVariantIds = getAddonVariantsSet(addons)
		Object.entries(carts).forEach(([id,cart])=>{
			childrenWithAddons[id] = new Set([])
			cart.lineItems.forEach(({productVariant})=>{
				if(productVariant){
					if(addonVariantIds.has(productVariant.id)){	
						childrenWithAddons[id].add(productVariant.id)
					}
				}
			})
		})
		setExistingAddons(childrenWithAddons)
	}

	useEffect(()=>{
		if(carts.init && carts.APIStatus === 'success' && initialized){
			getAddonsFromCart(carts.children).then(()=>{
				setShouldRender(true)
			})
		}
	}, [carts.init, initialized])

	const onSubmitAddons = async ()=>{
		const childrenCarts = deepClone(carts.children) as Record<ChildrenID, CartType>
		const addonVariantIds = getAddonVariantsSet(addons)
		const addonsToBeAdded = deepClone(existingAddons) as typeof existingAddons

		// delete add-ons, and determine which children need addons added to their cart
		Object.entries(childrenCarts).forEach(([childId, cart])=>{
			if(addonsToBeAdded[childId]){
				for(let i = 0; i < cart.lineItems.length; i++){
					const lineItem = cart.lineItems[i]
					if(!lineItem.product) continue
					const lineItemProductVariant = lineItem.productVariant?.id || ''
					// add-on is in cart, but shouldn't be
					if(
						addonVariantIds.has(lineItemProductVariant) &&
						!addonsToBeAdded[childId].has(lineItemProductVariant)
					){
						lineItem.quantity = 0
					}
					/**
					 * add-on is in cart, and should be, then we remove the
					 * id from the addons to be added to that user
					 */
					else if(
						addonVariantIds.has(lineItemProductVariant) &&
						addonsToBeAdded[childId].has(lineItemProductVariant)
					){
						addonsToBeAdded[childId].delete(lineItemProductVariant) 
					}
				}
			}
		})

		// add add-ons to child carts
		Object.entries(addonsToBeAdded).forEach(([childId, newAddons])=>{
			const childCart = childrenCarts[childId].lineItems
			newAddons.forEach((addonVariantID)=>{
				let addonVariant
				const product = addons.find((addon)=> (
					addon.variants.find((variant)=> {
						if(addonVariantID === variant.id){
							addonVariant = variant
							return true
						}
					})
				))
				if(product){
					childCart.push({
						productVariant: addonVariant,
						product,
						quantity: 1
					})
				}
			})
		})
		const responses = await Promise.all(
			Object.entries(childrenCarts).map(([_,cart])=>{
				return (
					dispatch(updateCartLineItems({
						cartId: cart.cartId,
						customerId: subscription.id,
						lineItems: cart.lineItems
					}))
				)
			})
		)

		for(let i = 0; i < responses.length; i++){
			if(isRejectedWithValue(responses[i])){
				return
			}
		}

		if(onSubmit){
			onSubmit()
		}
	}


	return {
		fields: {
			addons,
			existingAddons,
			shouldRender,
		},
		actions: {
			init,
			onSubmit: onSubmitAddons,
			setExistingAddons
		}
	}


}


export default AddonsFormViewController
