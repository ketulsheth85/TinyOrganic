import { VegetableIcon } from 'components/svg'
import React from 'react'

import MultipleChoiceQuestion from 'src/components/MultipleChoiceQuestion'


export interface HowDidYouHearFormProps{
	onSubmit?:(value?: string) => void
	loading?: boolean
}

/**
 * This Form will submit to a hardcoded endpoint, and will
 * call callback onSubmit function on success
 * @returns 
 */
const HowDidYouHearForm:React.FC<HowDidYouHearFormProps> = ({
	onSubmit,
	loading,
})=>{
	const choices = [
		{value: 'family-member', label: 'Family Member'},
		{value: 'friend', label: 'Friend'},
		{value: 'instagram', label: 'Instagram'},
		{value: 'facebook', label: 'Facebook'},
		{value: 'article-or-blog', label: 'News Article or Blog Post'},
		{value: 'google', label: 'Google'},
		{value: 'pinterest', label: 'Pinterest'},
	]

	const DEFAULT_VALUE = 'family-member'

	const _onSubmit = (value:string) => {
		// TODO: Add api submission here broski
		onSubmit && onSubmit(value)
	}

	return (
		<div className="HowDidYouHearForm">
			<MultipleChoiceQuestion
				defaultValue={DEFAULT_VALUE}
				loading={loading}
				HeaderImage={<VegetableIcon height={50} width={50} />}
				showOther
				question="How did you hear about us?"
				choices={choices}
				onSubmit={_onSubmit}
			/>
		</div>
	)
}

export default HowDidYouHearForm
