import React from 'react'
import cx from 'classnames'

import { classPrefixer } from 'src/utils/utils'

import './styles.scss'

export interface SmoothBoyCardProps{
	children: React.ReactNode
	imageURL?: string
	imageALT?: string
	className?: string
	bodyClasses?: string
}
const SmoothBoyCard:React.FC<SmoothBoyCardProps> = ({
	imageALT,
	imageURL,
	children,
	className,
	bodyClasses
})=>{
	const CLASS_NAME = 'SmoothBoyCard'
	const px = classPrefixer(CLASS_NAME)
	const classes = cx(CLASS_NAME, {
		[`${className}`]: !!className
	})
	const _bodyClasses = cx(px('body'), {
		[`${bodyClasses}`]: !!bodyClasses
	})
	return (
		<div className={classes}>
			{imageURL && (
				<div className={px('image')}>
					<img src={imageURL} alt={imageALT || ''} />
				</div>
			)}
			<div className={_bodyClasses}>
				{children}
			</div>
		</div>
	)
}

export default SmoothBoyCard
