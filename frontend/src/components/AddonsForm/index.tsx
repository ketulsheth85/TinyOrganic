import React, { useEffect } from 'react'
import { useSelector } from 'react-redux'

import { MultipageFormComponentProps } from 'src/shells/MultiPageForm'
import { RootState } from 'store/store'
import RenderAddonsForm from './components/RenderAddonsForm'
import AddonsFormViewController from './vc'

import './styles.scss'

const AddonsForm:React.FC<MultipageFormComponentProps> = ({
	shouldSeeQuestion,
	onBack,
	onSubmit,
}) => {
	const {subscription, carts} = useSelector((state:RootState)=> state)
	const {
		fields: {
			addons,
			existingAddons
		},
		actions,
	} = AddonsFormViewController(subscription, carts, onSubmit)

	const init = async ()=>{
		const _shouldSeeQuestion = shouldSeeQuestion(`
			It looks like you haven't gotten to "Addon details" just yet,
			please fill out the form below to continue 😊
		`)
		if(!_shouldSeeQuestion) return

		const addons = await actions.init()
		// if we fail to initilaize store, move on to next question
		if(!addons){
			onSubmit
		}
	}

	useEffect(()=>{
		init()
	},[])

	return (
		<RenderAddonsForm 
			subscription={subscription}
			carts={carts}
			addons={addons}
			existingAddons={existingAddons}
			setExistingAddons={actions.setExistingAddons}
			onBack={onBack}
			onSubmit={actions.onSubmit}
			title='Optional add-ons for the whole family!'
			subtitle='Please note: Tiny Toddler Meals are a recurring add-on that will be added to your subscription moving forward. Merch items are one-time add-ons that will be added to your next order only.'
		/>
	)
}

export default AddonsForm
