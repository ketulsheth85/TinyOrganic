import React, { useEffect } from 'react'
import { Button, Checkbox } from 'antd'
import { CheckboxValueType } from 'antd/lib/checkbox/Group'
import { MultipleChoiceQuestionChoice } from 'components/MultipleChoiceQuestion'
import FormWrapper, { ButtonContainer } from 'src/shells/FormWrapper'
import { deepClone } from 'src/utils/utils'

const CheckboxGroup = Checkbox.Group

export interface ChecklistQuestionProps{
	onSubmit: (childIds: Array<CheckboxValueType>) => void
	onBack?: ()=> void
	defaultChecked?: Array<CheckboxValueType>
	choices: Array<MultipleChoiceQuestionChoice>
	showCheckAll: boolean
	onBackText?: string
	onSubmitText?: string
	checkAllText?: string
}

const ChecklistQuestion:React.FC<ChecklistQuestionProps> = ({
	choices,
	checkAllText,
	showCheckAll,
	onBackText,
	onSubmitText,
	defaultChecked = [],
	onBack,
	onSubmit
}) => {
	const [checkedList, setCheckedList] = React.useState<Array<CheckboxValueType>>(deepClone(defaultChecked))
	const [checkAll, setCheckAll] = React.useState(false)

	useEffect(()=>{
		console.log('mounting modal')
	}, [])
  
	const onChange = (list:Array<CheckboxValueType>) => {
		setCheckedList(list)
		setCheckAll(list.length === choices.length)
	}
  
	const onCheckAllChange = (e:any) => {
		const options = choices.map(({value})=> value)
		setCheckedList(e.target.checked ? options : [])
		setCheckAll(e.target.checked)
	}

	const _onBack = ()=>{
		if(!onBack) return
		setCheckedList(deepClone(defaultChecked))
		onBack()
	}
  
	return (
		<FormWrapper className="OnboardingPageOverrides">
			{showCheckAll && (
				<Checkbox onChange={onCheckAllChange} checked={checkAll}>
					{checkAllText || 'Check all'}
				</Checkbox>
			)}
			<CheckboxGroup  options={choices} value={checkedList} onChange={onChange} />
			<ButtonContainer unstickyOnMobile>
				<Button type="primary" onClick={()=>{ onSubmit(checkedList) }}>
					{onSubmitText || 'Submit'}
				</Button>
				{onBack && (
					<Button type="default" onClick={()=>{ _onBack() }}>
						{onBackText || 'Back'}
					</Button>
				)}
			</ButtonContainer>
		</FormWrapper>
	)
}

export default ChecklistQuestion
