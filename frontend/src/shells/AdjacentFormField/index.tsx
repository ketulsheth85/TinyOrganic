import React from 'react'
import cx from 'classnames'

import './styles.scss'

interface AdjacentFormFieldProps{
    label?: string
    children?: React.ReactNode
	className?: string
}

const AdjacentFormField:React.FC<AdjacentFormFieldProps> = ({
	label,
	children,
	className = ''
})=>{
	const classes = cx('AdjacentFormField',{
		[className]: className
	})
	return (
		<div className={classes}>
			{label && (
				<p className='AdjacentFormField__label'>
					{label}
				</p>
			)}
			{children}
		</div>
	)
}

export default AdjacentFormField
