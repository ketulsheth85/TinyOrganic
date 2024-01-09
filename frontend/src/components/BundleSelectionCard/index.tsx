import React from 'react'
import cx from 'classnames'

import { StarIcon } from 'components/svg'

import './styles.scss'


interface BundleSelectionCardProps{
	featuredText?: string
	title: string
	subheader: string,
	text: string,
	active?: boolean
	onClick: ()=> void
}

const BundleSelectionCard:React.FC<BundleSelectionCardProps> = ({
	title,
	subheader,
	text,
	active,
	featuredText,
	onClick
})=>{

	const classes = cx('BundleSelectionCard', {
		'BundleSelectionCard--active': active
	})

	return (
		<div className={classes} onClick={onClick}>
			<div className="BundleSelectionCard__inner">
				{featuredText && (
					<p className="BundleSelectionCard__featured-text">
						<StarIcon />&nbsp;{featuredText}&nbsp;<StarIcon />
					</p>
				)}
				<h3 className="BundleSelectionCard__header">
					{title}
				</h3>
				<p className="BundleSelectionCard__subheader">
					{subheader}
				</p>
				<p className="BundleSelectionCard__text">
					{text}
				</p>
			</div>
		</div>
	)
}

export default BundleSelectionCard
