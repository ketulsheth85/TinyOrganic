import { useMemo, useState } from 'react'
import moment, {Moment} from 'moment-business-days'

import { CreateCustomerSubscriptionPayload, CustomerSubscription, CustomerSubscriptionStatus } from 'api/SubscriptionAPI/types'
import { reactivateSubscription, SubscriptionSliceState } from 'store/subscriptionSlice'
import { TWELVE_PACK_MEAL_PRICE, TWENTY_FOUR_PACK_MEAL_PRICE } from 'src/utils/constants'
import { ChildrenType } from 'api/ChildrenAPI/types'
import { dispatch } from 'store/store'
import { isRejectedWithValue, PayloadAction } from '@reduxjs/toolkit'
import { RenderSuccessToast } from 'components/Toast'
import { CartType, LineItemType } from 'api/CartAPI/types'
import { RenderChildOrderInfoViewControllerMembers } from '../RenderChildOrderInfo/vc'
import { defaultTo } from 'lodash'
import { FulfillmentStatus, OrderType } from 'api/OrderAPI/types'



type RenderChildWithSubscriptionViewControllerFields = {
	firstName: string
	childOrder: OrderType
	chargeDate: Moment
	receipesWithAllergies: Array<LineItemType>
	subscription: SubscriptionSliceState
	childSubscription: CustomerSubscription
	shouldHideHeaderInfo: boolean
	shouldShowDatePicker: boolean
	shouldShowChildInfo: boolean
	shouldShowAllergyWarningModal: boolean
	shouldShowReactiveSubscriptionModal: boolean
	currentSubscriptionTitle: string
	lastDateToMakeChanges: string
	isSubscriptionInactive: boolean
	childCart: CartType
	pricePerMeal: number
	shouldShowhowMealPlan: boolean
	childOrderItems: any
	subscriptionLineItems: Array<LineItemType>
}

type RenderChildWithSubscriptionViewControllerSetters = {
	hideMealPlan: ()=> void
	showMealPlan: ()=> void
	showChildInfoModal: ()=> void
	hideChildInfoModal: ()=> void
	showDatePicker: ()=> void
	reactiveChildSubscription: ()=> void
	hideAllergyWarningModal: ()=> void
	shouldShowRecipeWarningModal: (allergies: Array<string>)=> void
	getShippingDateCopy: (chargedAt?:string) => string
	setShouldShowReactivateSubcriptionModal: (show: boolean) => void
	updateBundleInfo: (payload: CreateCustomerSubscriptionPayload)  => Promise<PayloadAction<unknown>>
	updateChargeDate: (subscription: string, setShouldShowDatePicker:(showDatePicker: boolean) => void) => 
	({ chargeDate }: { chargeDate: Moment; }) => Promise<void>
	setShouldShowDatePicker: (show: boolean) => void
	onSubmitMealPlan: (hideMealPlan: () => void) => (cart: CartType) => Promise<void>
	getFulfillmentStatusToolTipText: (fulfillmentStatus:FulfillmentStatus) => string
}

export type RenderChildWithSubscriptionViewControllerMembers = {
	fields: RenderChildWithSubscriptionViewControllerFields
	actions: RenderChildWithSubscriptionViewControllerSetters
}

const RenderChildWithSubscriptionViewController = (
	child: ChildrenType,
	renderChildOrderInfoViewController: RenderChildOrderInfoViewControllerMembers,
):RenderChildWithSubscriptionViewControllerMembers =>{
	const { id, firstName } = child
	const { fields: { carts, subscription }, actions } = renderChildOrderInfoViewController


	const [shouldShowhowMealPlan, setShouldShowMealPlan] = useState(false)
	const [shouldShowDatePicker, setShouldShowDatePicker] = useState(false)
	const [shouldShowChildInfo, setShouldShowChildInfo] = useState(false)
	const [shouldShowAllergyWarningModal, setShouldShowAllergyWarningModal] = useState(false)
	const [shouldShowReactiveSubscriptionModal, setShouldShowReactivateSubcriptionModal] = useState(false)
	const [receipesWithAllergies, setRecipesWithAllergies] = useState<Array<LineItemType>>([])
	const childCart = carts.children[id]
	const childSubscription = subscription.subscriptions[id]
	const isSubscriptionInactive = useMemo(()=>(
		subscription.subscriptions[id].status === CustomerSubscriptionStatus.inactive
	),[subscription.subscriptions[id].status === 'active'])
	const hideMealPlan = ()=> setShouldShowMealPlan(false)
	const showMealPlan = ()=> setShouldShowMealPlan(true)
	const hideChildInfoModal = ()=> setShouldShowChildInfo(false)
	const showChildInfoModal = ()=> setShouldShowChildInfo(true)
	const showDatePicker = ()=> setShouldShowDatePicker(true)
	const hideAllergyWarningModal = ()=> setShouldShowAllergyWarningModal(false)
	const shouldHideHeaderInfo = useMemo(()=>(
		shouldShowhowMealPlan
	), [shouldShowhowMealPlan])
	const currentSubscriptionTitle = useMemo(()=>(
		!shouldHideHeaderInfo ? `${firstName}'s Subscription` : ''
	), [shouldHideHeaderInfo])
	const chargeDate = useMemo(()=>{
		return actions.getDefaultChargeDate(id)
	}, [[childSubscription.nextOrderChargeDate]])
	const lastDateToMakeChanges = useMemo(()=>{
		return chargeDate
			.subtract(1, 'days')
			.format('MM/DD/YYYY')
	}, [chargeDate.toString()])
	const subscriptionLineItems:Array<LineItemType> =  defaultTo(carts.children[id].lineItems, [])
	const childOrder = actions.getOrder(id)
	const childOrderItems = actions.getOrderLineItems(child.id)

	// We only offer 12 or 24 meal counts atm, so this implementation works
	const calculateMealPrice = (numberOfServings: number) =>{
		switch(numberOfServings){
		case 12:
			return TWELVE_PACK_MEAL_PRICE
		case 24:
			return TWENTY_FOUR_PACK_MEAL_PRICE
		default:
			return TWELVE_PACK_MEAL_PRICE
		}
	}
	
	const reactiveChildSubscription = ()=>{
		const childSubscription = subscription.subscriptions[id]
		dispatch(reactivateSubscription(childSubscription.id))
			.then((action)=>{
				if(isRejectedWithValue(action)){
					return
				}
				RenderSuccessToast('Subscription successfully updated')
				setShouldShowReactivateSubcriptionModal(false)
			})
	}

	const pricePerMeal = useMemo(()=>{
		return calculateMealPrice(childSubscription.numberOfServings)
	}, [childSubscription.numberOfServings])

	const getEstimatedShippingDates = (fromDate: string) => {

		moment.updateLocale('us', { workingWeekdays: [2, 3, 4, 5] })
	
		const earliestShippingDate: string = moment(fromDate).businessAdd(2).format('ddd MM/DD')
		const latestShippingDate: string = moment(fromDate).businessAdd(7).format('ddd MM/DD')
		return {
			earliestShippingDate,
			latestShippingDate,
		}
	}

	const getShippingDateCopy = (chargedAt?:string) =>{
		if(chargedAt){
			const {
				earliestShippingDate,
				latestShippingDate
			} = getEstimatedShippingDates(chargedAt)

			return `${earliestShippingDate} - ${latestShippingDate}`
		}

		return 'We are processing your order and will have this information soon.'
	}

	const getFulfillmentStatusToolTipText = (fulfillmentStatus:FulfillmentStatus) =>{
		switch(fulfillmentStatus){
		case FulfillmentStatus.pending:
			return 'Your order is being processed or has been shipped'
		case FulfillmentStatus.cancelled:
			return 'Your order has been cancelled'
		case FulfillmentStatus.fulfilled:
			return 'Your order has been succesfully delivered'
		case FulfillmentStatus.partial:
			return 'Part of your order has arrived'
		default: 
			return 'Part of your order has arrived'
		}
	}

	const _calculateRecipesWithAllergies = (allergies: Array<string>)=>{
		const childAllergySet = new Set(allergies)
		const _receipesWithAllergies = subscriptionLineItems.filter(({product})=>{
			return product.ingredients && product.ingredients
				.find((ingredient)=> childAllergySet.has(ingredient.name))
		})
		setRecipesWithAllergies(_receipesWithAllergies)
		return _receipesWithAllergies
	}

	const shouldShowRecipeWarningModal = (allergies: Array<string>)=>{
		const _receipesWithAllergies = _calculateRecipesWithAllergies(allergies)
		setShouldShowAllergyWarningModal(_receipesWithAllergies.length > 0)
	}


	return {
		fields: {
			firstName,
			childOrder,
			shouldShowChildInfo,
			subscription: renderChildOrderInfoViewController.fields.subscription,
			chargeDate,
			receipesWithAllergies,
			childSubscription,
			shouldHideHeaderInfo,
			shouldShowDatePicker,
			shouldShowAllergyWarningModal,
			shouldShowReactiveSubscriptionModal,
			currentSubscriptionTitle,
			lastDateToMakeChanges,
			isSubscriptionInactive,
			childCart,
			pricePerMeal,
			shouldShowhowMealPlan,
			childOrderItems,
			subscriptionLineItems
		},
		actions: {
			hideMealPlan,
			showMealPlan,
			hideChildInfoModal,
			showChildInfoModal,
			showDatePicker,
			getShippingDateCopy,
			reactiveChildSubscription,
			hideAllergyWarningModal,
			setShouldShowReactivateSubcriptionModal,
			updateBundleInfo: renderChildOrderInfoViewController.actions.updateBundleInfo,
			updateChargeDate: actions.updateChargeDate,
			setShouldShowDatePicker,
			onSubmitMealPlan: renderChildOrderInfoViewController.actions.onSubmitMealPlan,
			getFulfillmentStatusToolTipText,
			shouldShowRecipeWarningModal,
		}
	}
}

export default RenderChildWithSubscriptionViewController
