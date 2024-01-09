import React, { useCallback, useMemo } from 'react'
import { Route, Switch} from 'react-router'

import { SplashPage } from 'components/OnboardingSplashPage'
import MultiPageForm from 'src/shells/MultiPageForm'
import useOnboardingPageViewModel from './vc'
import { MultipageFormQuestion } from 'src/config/onboarding'
import DiscountBanner from 'components/DiscountBanner'

/**
 * Main page of onboarding routing, this page is responsible for
 * Determining the onboarding question that should be shown based
 * on the route and rendering what steps a user can see
 */
const OnboardingForm:React.FC = ()=>{
	const vc = useOnboardingPageViewModel()

	const setStep = useCallback(()=> vc.setStep, [])
	const steps = useMemo(()=> vc.steps, [])

	// show splash page while we determine route
	if(!vc.routeDetermined){
		return (
			<SplashPage />
		)
	}

	return(
		<>
			{vc.discount && (
				<DiscountBanner 
					bannerText={vc.discount.bannerText} 
					codename={vc.discount.codename}
				/>
			)}
			<MultiPageForm
				onSetStep={setStep}
				steps={steps}
				currentStep={vc.step}
			>
				<Switch>
					{Object.entries(vc.questions).map(([,question])=>{
						const {id,Component} = question as MultipageFormQuestion
						const _onBack = vc.currentQuestion.prev && vc.onBack
						const path = `${vc.url}/${id}`
						return (
							<Route 
								key={`onboarding-question-${id}`}
								path={path}
								exact
							>
								<Component
									shouldSeeQuestion={vc.shouldSeeQuestion(id)} 
									onBack={_onBack}
									onSubmit={vc.onSubmit}
								/>
							</Route>
						)
					})}
				</Switch>
			</MultiPageForm>
		</>
	)

}


export default OnboardingForm
