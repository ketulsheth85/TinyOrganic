import React, { useState } from 'react'
import { Button, Input, Radio, RadioChangeEvent, Space } from 'antd'

import FormWrapper, { ButtonContainer } from 'src/shells/FormWrapper'

import './styles.scss'

export type MultipleChoiceQuestionChoice = {
	label: string
	value: string
}
export interface MultipleChoiceQuestionProps{
	HeaderImage?: React.ReactNode
	question: string,
	loading?: boolean,
	defaultValue?: string
	choices: Array<MultipleChoiceQuestionChoice>
	onSubmit: (value: string) => void
	showOther?: boolean
}

const MultipleChoiceQuestion:React.FC<MultipleChoiceQuestionProps> = ({
	HeaderImage,
	question,
	choices,
	showOther,
	defaultValue,
	loading,
	onSubmit
})=>{

	const [choice, setChoice] = useState(defaultValue || '')
	const [otherText, setOtherText] = useState('')

	const onClick = (e:RadioChangeEvent)=>{
		setChoice(e.target.value)
	}

	const onChange = (e:React.ChangeEvent<HTMLInputElement>)=>{
		const value = e.target.value
		setOtherText(value)
	}

	const _onSubmit = ()=>{
		let value = choice
		const _otherText = otherText.replace(/\s/g, '')
		if(value === 'other' && _otherText.length > 0){
			value = _otherText
		}
		onSubmit(value)
	}

	return (
		<FormWrapper
			className="MultiChoiceQuestion OnboardingPageOverrides"
			HeaderImage={HeaderImage}
			subtitle={question}
			loading={loading}
		>
			<Radio.Group onChange={onClick} value={choice}>
				<Space direction="vertical">
					{
						choices.map(({value,label})=>{
							return (
								<Radio key={`${value}-${label}`} value={value}>{label}</Radio>
							)
						})
					}
					{showOther && (
						<Radio value="other">
									Other
							{choice === 'other' ? 
								<Input 
									onChange={onChange} 
									placeholder='Enter Option'
									style={{ width: 200, marginLeft: 10 }} /> : null
							}
						</Radio>
					)}
				</Space>
			</Radio.Group>
			<ButtonContainer unstickyOnMobile>
				<Button disabled={loading} onClick={_onSubmit} type="primary">
					Submit
				</Button>
			</ButtonContainer>
		</FormWrapper>
	)
}

export default MultipleChoiceQuestion
