import React from 'react'
import { Button } from 'antd'

export interface RenderChildOrderButtons{
	childName: string
	isSubscriptionInactive?: boolean
	onEditOrderDate: ()=> void
	onEditMeals: () => void
	onEditChildInfo: () => void
}
const RenderChildOrderButtons:React.FC<RenderChildOrderButtons> = ({
	childName,
	onEditOrderDate,
	onEditMeals,
	onEditChildInfo,
	isSubscriptionInactive
})=>{
	return (
		<div className="DashboardPlanForm__options">
			{!isSubscriptionInactive && (
				<Button onClick={onEditOrderDate} type="text">Change Charge Date</Button>
			)}
			<Button onClick={onEditMeals} type="text">Edit Meal Plan</Button>
			<Button onClick={onEditChildInfo} type="text">Update {childName}&apos;s Profile</Button>
		</div>
	)
}

export default RenderChildOrderButtons
