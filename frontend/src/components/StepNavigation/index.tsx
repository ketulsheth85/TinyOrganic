import React from 'react'
import { 
	Steps,
	Form,
	Select
} from 'antd'
import { CaretDownOutlined } from '@ant-design/icons'

import './styles.scss'

const { Step } = Steps

export interface StepNavigationStep{
	title: string
	rootQuestion: string
	disabled?: boolean
}

export interface StepNavigationProps{
	currentStep: number
	onSetStep: (current: number) => void
	steps: Array<StepNavigationStep>
}

const StepNavigation:React.FC<StepNavigationProps> = ({
	currentStep,
	onSetStep,
	steps
}) => {

	return (
		<>
			<Form.Item
				className="StepNavigationMobile"
				wrapperCol={{span: 24}}
				initialValue={currentStep}
			>
				<Select
					className="HouseHoldInfoForm__input__field"
					placeholder="Select an Option"
					onChange={onSetStep}
					value={currentStep}
					suffixIcon={<CaretDownOutlined style={{color: '#204041'}} />}
				>
					{/* This map function cannot be it's own component as the Select 
					Component expects a Selection.Option as a child */}
					{
						steps && steps.map((item, idx) => (
							<Select.Option 
								key={item.title} 
								title={item.title} 
								value={idx}
								disabled={item.disabled}
							>
								{item.title}
							</Select.Option>
						))
					}
				</Select>
			</Form.Item>
			<Steps className="StepNavigation" current={currentStep} onChange={onSetStep}>
				{/* Step component won't render unless it is a direct child of Steps component */}
				{steps.map(item => (
					<Step 
						key={item.title} 
						title={item.title} 
						disabled={item.disabled}
					/>
				))}
			</Steps>
		</>
	)
}

export default StepNavigation
