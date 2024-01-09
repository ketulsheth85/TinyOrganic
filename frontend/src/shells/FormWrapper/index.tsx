import React from 'react'
import { 
	Card,
	Col,
	Row,
	Form
} from 'antd'
import cx from 'classnames'
import { BeatLoader } from 'react-spinners'

import './styles.scss'
import { TinyP } from 'components/Typography'


interface FormWrapperProps{
	HeaderImage?: React.ReactNode
	tagline?: string
    title?: string,
    subtitle?: string,
	children?: React.ReactNode
	className?: string,
	loading?: boolean
}

const FormWrapper:React.FC<FormWrapperProps> = ({
	HeaderImage,
	tagline,
	title,
	subtitle,
	children,
	className,
	loading,
})=>{

	const classes = cx('FormWrapper',{
		[className as string]: className
	})

	return (
		<Card className={classes}>
			<Row>
				{(title || subtitle || HeaderImage || tagline) && (
					<>
						<Col className='FormWrapper__header-container' span={24}>
							{HeaderImage && (
								<div className='FormWrapper__header-image'>
									{HeaderImage}
								</div>
							)}
							{true && (
								<TinyP 
									className={`
										text-center
										font-supria-sans
										color-pink-dark
										font-16
										font-italic
										weight-600
									`}
								>
									{tagline}
								</TinyP>
							)}
							{title && (
								<h1 className="FormWrapper__header-container__title">
									{title}
								</h1>
							)}
							{subtitle && (
								<h5 className="FormWrapper__header-container__subtitle">
									{subtitle}
								</h5>
							)}
						</Col>
					</>
				)}
				{children}
				{loading && (
					<div className="FormWrapper__loading-icon">
						<BeatLoader color='#204041' size={20} margin={4}/>
					</div>
				)}
			</Row>
		</Card>
	)
}

export default FormWrapper

export interface ButtonContainerProps{
	className?: string
	children: React.ReactNode
	unstickyOnMobile?: boolean
}

export const ButtonContainer:React.FC<ButtonContainerProps> = ({
	className,
	children,
	unstickyOnMobile
})=>{
	const classes = cx('ButtonContainer', {
		'ButtonContainer--unsticky': unstickyOnMobile,
		[`${className}`]: !!className
	})

	const spacingClasses = cx('ButtonContainerSpacing', {
		'ButtonContainerSpacing--unsticky': unstickyOnMobile,
	})
	return (
		<>
			<div className={spacingClasses}></div>
			<Form.Item 
				wrapperCol={{ span: 24 }}
				className={classes}
			>
				{children}
			</Form.Item>
		</>
	)
}
