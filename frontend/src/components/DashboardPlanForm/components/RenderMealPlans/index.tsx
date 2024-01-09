import React from 'react'

import { ChildMealSelectionForm, ChildMealSelectionFormProps } from 'components/MealSelectionForm'

const RenderMealPlan:React.FC<ChildMealSelectionFormProps> = (props)=>{
	return (
		<ChildMealSelectionForm
			{...props}
			backText="Cancel"
			submitText="Update Subscription"
		/>
	)
}

export default RenderMealPlan
