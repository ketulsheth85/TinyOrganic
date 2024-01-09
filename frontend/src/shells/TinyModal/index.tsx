import React from 'react'
import { Modal, ModalProps } from 'antd'
import cx from 'classnames'

export interface TinyModalProps extends ModalProps{
	title?: string
	isModalVisible: boolean
	className?: string
	children?: React.ReactNode
	closable?: boolean
	footer?: React.ReactNode
	defaultFooter?: boolean
	onCancel?: ()=> void
}
const TinyModal:React.FC<TinyModalProps> = ({
	className,
	title,
	isModalVisible,
	children,
	closable = true,
	footer = null,
	defaultFooter,
	onCancel,
	...rest
})=>{
	const classes = cx('',{
		[`${className}`]: !!className
	})

	return (
		<>
			<Modal
				className={classes}
				title={title}
				visible={isModalVisible} 
				closable={closable}
				onCancel={onCancel}
				{...(!defaultFooter && {footer})}
				{...rest}
			>
				{children}
			</Modal>
		</>
	)
}

export default TinyModal
