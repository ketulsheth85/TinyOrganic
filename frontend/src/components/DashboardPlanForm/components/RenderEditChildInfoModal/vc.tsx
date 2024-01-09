import { useState } from 'react'
import { isRejectedWithValue } from '@reduxjs/toolkit'

import { ChildrenType, ChildrenUpdatePayload } from 'api/ChildrenAPI/types'
import { RenderSuccessToast } from 'components/Toast'
import { dispatch } from 'store/store'
import { updateChild } from 'store/subscriptionSlice'

type RenderEditInfoModalViewControllerFields = {
	loading?: boolean
}

type RenderEditInfoModalViewControllerSetters = {
	onSubmit: (child:ChildrenUpdatePayload) => void,
}

export type RenderEditInfoModalViewControllerMembers = {
	fields: RenderEditInfoModalViewControllerFields
	actions: RenderEditInfoModalViewControllerSetters
}


const RenderEditInfoModalViewController = (
	onSubmit: (allergies: Array<string>)=> void,
):RenderEditInfoModalViewControllerMembers =>{
	const [loading, setLoading] = useState(false)

	const onSubmitForm = (child:ChildrenUpdatePayload)=>{
		setLoading(true)
		dispatch(updateChild(child))
			.then((action)=>{
				if(isRejectedWithValue(action)) return
				const payload = action.payload as ChildrenType
				onSubmit((payload.allergies || []).map(({name})=> name))
				RenderSuccessToast('Successfully updated child info')
			})
			.finally(()=>{
				setLoading(false)
			})
	}
	return {
		fields: {
			loading,
		},
		actions:{
			onSubmit: onSubmitForm,
		}
	}
}

export default RenderEditInfoModalViewController
