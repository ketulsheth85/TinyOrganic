import React from 'react'

import StepNavigation,{
	StepNavigationProps
} from 'components/StepNavigation'
import './styles.scss'

import Footer from 'components/Footer'

export interface MultipageFormComponentProps{
	store: any
	shouldSeeQuestion: (redirectMessage?: string) => boolean
	onSubmit: (shouldLoop?: boolean)=> void
	onBack?: (shouldLoop?: boolean) => void
}

export interface MultipageFormQuestion{
  step: number
  id: string,
	prev?: string
  next?: string,
  Component: React.FC<any>
}

export interface MultiPageFormBodyProps extends MultipageFormComponentProps{
    questions: Record<string, MultipageFormQuestion>
}

export const MultiPageFormBody:React.FC<MultiPageFormBodyProps> = ({
	questions,
	store,
	onSubmit,
	onBack
})=>{
	const Component = questions[store.currentQuestion].Component
	const _onBack = questions[store.currentQuestion].prev && onBack
	return(
		<>
			<Component 
				store={store} 
				onSubmit={onSubmit}
				onBack={_onBack}
			/>
		</>
	)
}

// eslint-disable-next-line @typescript-eslint/no-empty-interface
export interface MultipageFormProps extends StepNavigationProps {}

const MultiPageForm:React.FC<MultipageFormProps> = ({
	children,
	currentStep,
	onSetStep,
	steps,
})=>{
	
	return (
		<div className="MultiPageForm">

			<div className="MultiPageForm__navigation">
				<div className="MultiPageForm__navigation__inner">
					<div className="MultiPageForm__navigation__inner__logo">
						<a href="/">
							<img
								src="https://cdn.shopify.com/s/files/1/0018/4650/9667/files/TINY-fullcolor-xwhitespace.png?v=1585325388" 
								alt=""
							/>
						</a>
					</div>
					<StepNavigation
						currentStep={currentStep}
						onSetStep={onSetStep}
						steps={steps}
					/>
				</div>
			</div>
			<div className="MultiPageForm__inner">
				{children}
			</div>
			<Footer/>
		</div>
	)
}

export default MultiPageForm
