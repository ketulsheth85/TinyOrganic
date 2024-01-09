import { isRejectedWithValue } from '@reduxjs/toolkit'
import { isEmpty } from 'lodash'
import { useEffect, useState } from 'react'
import { useSelector } from 'react-redux'
import { useHistory, useRouteMatch } from 'react-router'

import { 
	DEFAULT_QUESTION, 
	MultipageFormQuestion, 
	questions, 
	steps as onboardingSteps,
	StepsNum 
} from 'src/config/onboarding'
import { deepClone } from 'src/utils/utils'
import { dispatch, RootState } from 'store/store'
import { initStore as initSubscriptionStore, SubscriptionSliceState } from 'store/subscriptionSlice'
import { initStore as initCartStore } from 'store/cartSlice'
import { RenderDefaultToast } from 'components/Toast'
import { TOP_CENTER_PERSISTENT_TOAST_OPTIONS } from 'src/utils/constants'
import useDiscountMethods from 'src/hooks/useDiscountMethods'
import { Discount } from 'api/DiscountAPI/types'
import useYotpoMethods from 'src/hooks/useYotpoMethods'

/**
 * View Controller
 */
const useOnboardingPageViewController = ()=>{
	const subscription = useSelector((state:RootState)=> state.subscription)
	const carts = useSelector((state:RootState)=> state.carts)
	const {url} = useRouteMatch()
	const [routeDetermined, setRouteDetermined] = useState(false)
	const [step, setStep] = useState(0)
	const [steps, setSteps] = useState(onboardingSteps)
	const history = useHistory()
	const [currentQuestion, setCurrentQuestion] = useState<MultipageFormQuestion>(DEFAULT_QUESTION)
	const [redirectMessage, setRedirectMessage] = useState('')
	const [discount, setDiscount] = useState<Discount | undefined>()
	const yotpoMethods = useYotpoMethods()

	const discountMethods = useDiscountMethods()

	const getRoute = (url:string,pathname:string) => pathname.replace(`${url}/`, '')

	const constructPath = (route:string) => `${url}/${route}${history.location.search}`
		.replace(/\/\//g, '/')

	const _setStep = (num:number)=>{
		const stepToSet = steps.find(({id})=> id === num)
		if(stepToSet){
			setPath(stepToSet.rootQuestion)
			setStep(num)
		}
	}

	const _setSteps = (payload?:SubscriptionSliceState)=>{
		const _steps = deepClone(steps) as typeof steps
		const _payload = payload || subscription
		const meAndMyKids = !!_payload.id
		const myFirstBox = _payload.status == 'plan_selection'
		const checkout = _payload.status === 'checkout'

		_steps.forEach((st)=>{
			if(st.id === StepsNum.ME_AND_MY_KIDS){
				st.disabled = !meAndMyKids && !myFirstBox && !checkout
			}
			else if(st.id === StepsNum.MY_FIRST_BOX){
				st.disabled = !myFirstBox && !checkout
			}
			else if(st.id === StepsNum.CHECKOUT){
				st.disabled = !checkout
			}
		})
		setSteps(_steps)
	}

	const shouldSeeHouseHoldInfo = ()=> subscription.id 
	const shouldSeeChildrenInfo =  ()=>{
		if(!shouldSeeHouseHoldInfo() || subscription.children.length === 0){
			return false
		}
		for(let i = 0; i < subscription.children.length; i++){
			if(!subscription.children[i].id) return false
		}
		return true		
	}
	const shouldSeeBundleInfo = ()=>{
		if(!shouldSeeChildrenInfo()) return false

		for(let i = 0; i < subscription.children.length; i++){
			if(!subscription.children[i].birthDate) return false
		}
		return true
	}
	const shouldSeeMealSelection = ()=>{
		if(!shouldSeeBundleInfo()) return false

		const {children, subscriptions} = subscription
		for(let i = 0; i < children.length; i++){
			const id = children[i].id
			if(!subscriptions[id]) return false
		}
		return true
	}
	const shouldSeeAddons = ()=>{
		if(!shouldSeeMealSelection()) return false
		const {children} = subscription
		const childCarts = carts.children
		if(children.length < childCarts.length){
			return false
		}
		for(let i = 0; i < children.length; i++){
			const id = children[i].id
			if(
				!childCarts[id] || 
				childCarts[id].lineItems.length === 0
			){
				return false
			}
		}
		return true
	}
	/**
	 * Addons are an optional step before checkout,
	 * so if we can see addons, we can see checkout
	 */
	const shouldSeeCheckout = ()=> shouldSeeAddons()

	/**
	 * Gets a list of question user is able to see.
	 * 
	 * Calculating this for every page is slow,
	 * but users deleting children can lead to
	 * unexpected behavior otherwise, and this
	 * is simpler than covering a bunch of edge
	 * cases around missing children
	 */
	const getUserProgress = ()=>{
		const userProgress = ['account_info']
		if(!shouldSeeHouseHoldInfo()) return userProgress
		userProgress.push('household_info')
		if(!shouldSeeChildrenInfo()) return userProgress
		userProgress.push('children_info')
		if(!shouldSeeBundleInfo()) return userProgress
		userProgress.push('bundle_info')
		if(!shouldSeeMealSelection()) return userProgress
		userProgress.push('meal_selection')
		if(!shouldSeeAddons()) return userProgress
		userProgress.push('add_ons')
		if(!shouldSeeCheckout()) return userProgress
		userProgress.push('checkout')
		return userProgress
	}
	/**
	 * Helper for shouldSeeQuestion
	 * @param question id of question to check
	 * @param redirectMessage optional message that will
	 * render default toast. Toast will only render if 
	 * message is included
	 */
	const _shouldSeeQuestion = (question: string, redirectMessage?:string)=>{
		const userProgress = getUserProgress()
		const userHasSeenQuestion = new Set(userProgress).has(question)
		if(!userHasSeenQuestion){
			history.push(constructPath(userProgress[userProgress.length-1]))
			if(redirectMessage) setRedirectMessage(redirectMessage)
		}
		return userHasSeenQuestion
	}
	/**
	 * Checks if user should see the current question, if
	 * user should not see question, it will redirect them
	 * to the latest question.
	 * 
	 * This assumes that the cart and subscription stores
	 * have succesfully loaded.
	 * @param question id of current question
	 */
	const shouldSeeQuestion = (question: string)=>{
		if(!questions[question]){
			history.push(constructPath('account_info'))
		}

		return (redirectMessage?:string) => (
			_shouldSeeQuestion(question, redirectMessage)
		)
	}

	/**
	 * Initializes data stores necessary for
	 * view controller to do its job.
	 * 
	 * @returns true if stores initialized succesfully,
	 * false otherwise 
	 */
	const initStores = async ()=>{
		const initSubcriptionAction = await dispatch(initSubscriptionStore())
		if(isRejectedWithValue(initSubcriptionAction) || isEmpty(initSubcriptionAction.payload)){
			return false
		}
		const subscriptionPayload = initSubcriptionAction.payload as SubscriptionSliceState
		const initCartStoreAction = await dispatch(initCartStore(subscriptionPayload.id))
		if(isRejectedWithValue(initCartStoreAction)){
			return false
		}
		return true
	}

	const initDiscountBanner = async (): Promise<void>=>{
		let discount =  await yotpoMethods
			.actions
			.getDiscountFromReferralLink()

		if(!discount){
			discount = await discountMethods
				.getPrimaryDiscount()
		}

		if(discount){
			setDiscount(discount)
		}
		return 
	}

	const init = async ()=>{
		await initDiscountBanner()
		const route = getRoute(url, history.location.pathname)
		const [pageRoute, question] = Object.entries(questions).find(([id])=> (
			id === route
		)) || [DEFAULT_QUESTION.id, DEFAULT_QUESTION]
		
		let shouldRedirectToDefault = false
		if(question !== DEFAULT_QUESTION){
			shouldRedirectToDefault = !(await initStores())
		}

		/**
		 * If a user tries to access a page they are have not seen yet,
		 * they are not logged in, or there was an error rendering the page,
		 * prompt them to log in and to pick up where they left off
		 */
		if(shouldRedirectToDefault){
			setCurrentQuestion(DEFAULT_QUESTION)
			setRouteDetermined(true)
			history.push(constructPath(DEFAULT_QUESTION.id))
			setRedirectMessage(`
				It looks like you have an application in progress.
				fill out the form below and pick up where you left off 😊
			`)
			return
		}

		setRouteDetermined(true)
		setCurrentQuestion(question)
		setStep(question.step)
		history.push(constructPath(pageRoute))
	}

	const setPath = (questionId:string) =>{
		const question = questions[questionId]
		if(question){
			history.push(constructPath(questionId))
		}
	}

	const onSubmit = ()=>{
		const {next} = currentQuestion
		if(next){
			setPath(next)
		}
	}

	const onBack = () =>{
		const {prev} = currentQuestion
		if(prev){
			setPath(prev)
		}
	}

	/**
	 * Fetch necessary data and determine route
	 */
	useEffect(()=>{
		init()
	},[])

	/**
	 * Recalculate steps when susbcription is updated
	 */
	useEffect(()=>{
		_setSteps(subscription)
	}, [subscription])

	/**
	 * keep current question in sync with current question
	 * state
	 */
	useEffect(()=>{
		const questionId = history.location.pathname.replace(`${url}/`, '')
		const question = questions[questionId]
		if(question){
			setStep(question.step)
			setCurrentQuestion(question)
		}
	},[history.location.pathname])

	/**
	 * render redirect message modal if a redirect message is set
	 */
	useEffect(()=>{
		if(redirectMessage){
			const onClose = ()=> setRedirectMessage('')
			RenderDefaultToast(redirectMessage, 
				{...TOP_CENTER_PERSISTENT_TOAST_OPTIONS, onClose:onClose}
			)
		}
	}, [redirectMessage])


	return {
		url,
		step,
		setStep: _setStep,
		steps: steps || [],
		questions,
		discount,
		currentQuestion,
		setCurrentQuestion,
		shouldSeeQuestion,
		routeDetermined,
		onSubmit,
		onBack,
	}
} 

export default useOnboardingPageViewController
