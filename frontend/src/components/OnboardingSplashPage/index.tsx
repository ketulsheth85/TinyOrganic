import React from 'react'
import { GridLoader } from 'react-spinners'

import './styles.scss'

import { MultipageFormComponentProps } from 'src/shells/MultiPageForm'

const OnboardingSplashPage:React.FC<MultipageFormComponentProps> = ()=>{
	return (
		<SplashPage />
	)
}

export default OnboardingSplashPage


export const SplashPage:React.FC = ()=>{
	return (
		<div className="OnboardingSplashPage">
			<div className="OnboardingSplashPage__inner">
				<div className="OnboardingSplashPage__inner__spinner">
					<GridLoader color='#204041' size={20} margin={4}/>
				</div>
			</div>
		</div>
	)
}
