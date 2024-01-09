/* eslint-disable @typescript-eslint/explicit-module-boundary-types */
// eslint-disable-next-line no-undef
const prod = process.env.NODE_ENV === 'production'

const prodAnalytics = window.analytics
const fakeAnalyticsFunction = async (...args)=> {
	if(!prod) console.log(args)
}
const fakeAnalytics = {
	page: fakeAnalyticsFunction,
	identify: fakeAnalyticsFunction,
	track: fakeAnalyticsFunction
}

// guard rail for analytics
const analytics = ()=>{
	if(window && window.analytics){
		return prodAnalytics
	}
	return fakeAnalytics
}

/**
 * All of these should be called with an info object that contains
 * first_name, last_name, and email for the current user
 */
const analyticsClient = {
	pageView: (category, name, info={}) =>{
		try{
			return analytics().page(category, name, info)
		}
		catch(e){
			return new Promise((resolve)=>{
				resolve()
			})
		}
	},
	selectedPlan: (info) => {
		try{
			return analytics().track('Selected Plan', info)
		} catch (e) {
			return new Promise((resolve)=>{
				resolve()
			})
		}
	},
	addedDiscountCodeToInitialOrder: (info) => {
		try {
			return analytics().track('Added Discount to Initial Order', info)
		} catch(e){
			return new Promise((resolve)=>{
				resolve()
			})
		}
	},
	selectedMeals: (info) => {
		try {
			return analytics().track('Selected Meals', info)
		} catch(e){
			return new Promise((resolve)=>{
				resolve()
			})
		}
	},
	addedChild: (info) => {
		try{
			return prodAnalytics.track('Added Child Information', info)
		}
		catch(e){
			return new Promise((resolve)=>{
				resolve()
			})
		}
	},
	addToCart: (info) =>{
		try{
			return analytics().track('Add To Cart', info)
		}
		catch(e){
			return new Promise((resolve)=>{
				resolve()
			})
		}
	},
	addedAddress: async (info)=>{
		try{
			return await analytics().track('Added Shipping Address', info)
		}
		catch(e){
			return new Promise((resolve)=>{
				resolve()
			})
		}
	},
	updatedAddress: async (info)=>{
		try{
			return await analytics().track('Updated Shipping Address', info)
		}
		catch(e){
			return new Promise((resolve)=>{
				resolve('')
			})
		}
	},
	addedPaymentInformation: async (info)=>{
		try{
			return await analytics().track('Added Payment Information', info)
		}
		catch(e){
			return new Promise((resolve)=>{
				resolve('')
			})
		}
	},
	updatedPaymentInformation: (user)=> {
		try{
			return analytics().track('Updated Payment Information', user)
		}
		catch(e){
			return new Promise((resolve)=>{
				resolve('')
			})
		}
	},
	updateBundleInfo: async (info)=> {
		try{
			return await analytics().track('Update Meal Plan Selection',info)
		}
		catch(e){
			return new Promise((resolve)=>{
				resolve('')
			})
		}
	},
	updateSubscription: async (info)=> {
		try{
			return await analytics().track('Updated Plan', info)
		}
		catch(e){
			return new Promise((resolve)=>{
				resolve('')
			})
		}
	},
	startedCheckout: (info)=>{
		try{
			return analytics().track('Started Checkout', info)
		}
		catch(e){
			return new Promise((resolve)=>{
				resolve('')
			})
		}
	},
	completedCheckout: (info)=>{
		try{
			return analytics().track('Completed Checkout', info)
		} catch (e){
			return new Promise((resolve) => {
				resolve('')
			})
		}
	},
	subscriptionInitiated: (info) => {
		try {
			return analytics().track('Subscription Initiated', info)
		} catch (e){
			return new Promise((resolve) => {
				resolve('')
			})
		}
	},
	identify: (userId, traits = {}) => {
		try {
			return analytics().identify(userId, traits)
		} catch (e){
			return new Promise((resolve) => {
				resolve('')
			})
		}
	}
}


export default analyticsClient
