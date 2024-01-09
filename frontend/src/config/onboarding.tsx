import AccountInfoForm from 'components/AccountInfoForm'
import AddonsForm from 'components/AddonsForm'
import ChildrenInfoForm from 'components/ChildrenInfoForm/index.tsx'
import BundleSelectionForm from 'components/BundleSelectionForm'
import CheckoutForm from 'components/CheckoutForm'
import HouseHoldInfoForm from 'components/HouseHoldInfoForm'
import MealSelectionForm from 'components/MealSelectionForm'
import { camelCaseToTitleCase } from 'src/utils/utils'

export enum Steps{
	ME_AND_MY_KIDS = 'ME_&_MY_KIDS',
	MY_FIRST_BOX = 'MY_FIRST_BOX',
	CHECKOUT = 'CHECKOUT',
}

/** Enums not available at build time sometimes */
export const StepsNum ={
	ME_AND_MY_KIDS: 0,
	MY_FIRST_BOX: 1,
	CHECKOUT: 2,
}

export interface MultipageFormQuestion{
	step: number
	id: string,
	prev?: string
	next?: string,
	Component: React.FC<any>
  }

export const questions:Record<string, MultipageFormQuestion> = {
	account_info: {
		step: StepsNum.ME_AND_MY_KIDS,
		id: 'account_info',
		next: 'household_info',
		Component: AccountInfoForm
	},
	household_info: {
		step: StepsNum.ME_AND_MY_KIDS,
		id: 'household_info',
		prev: 'account_info',
		next: 'children_info',
		Component: HouseHoldInfoForm
	},
	children_info: {
		step: StepsNum.ME_AND_MY_KIDS,
		id: 'children_info',
		prev: 'household_info',
		next: 'bundle_info',
		Component: ChildrenInfoForm
	},
	bundle_info: {
		step: StepsNum.MY_FIRST_BOX,
		id: 'bundle_info',
		prev: 'children_info',
		next: 'meal_selection',
		Component: BundleSelectionForm
	},
	meal_selection: {
		step: StepsNum.MY_FIRST_BOX,
		id: 'meal_selection',
		prev: 'bundle_info',
		next: 'add_ons',
		Component: MealSelectionForm
	},
	add_ons: {
		step: StepsNum.MY_FIRST_BOX,
		id: 'add_ons',
		prev: 'meal_selection',
		next: 'checkout',
		Component: AddonsForm
	},
	checkout: {
		step: StepsNum.CHECKOUT,
		id: 'checkout',
		prev: 'meal_selection',
		Component: CheckoutForm
	}
}

export const steps = [
	{
		id: StepsNum.ME_AND_MY_KIDS,
		title: camelCaseToTitleCase(Steps.ME_AND_MY_KIDS),
		rootQuestion: questions.household_info.id,
		disabled: true
	},
	{
		id: StepsNum.MY_FIRST_BOX,
		title: camelCaseToTitleCase(Steps.MY_FIRST_BOX),
		rootQuestion: questions.bundle_info.id,
		disabled: true
	},
	{
		id: StepsNum.CHECKOUT,
		title: camelCaseToTitleCase(Steps.CHECKOUT),
		rootQuestion: questions.checkout.id,
		disabled: true,
	}
]

export const DEFAULT_QUESTION = questions.account_info
