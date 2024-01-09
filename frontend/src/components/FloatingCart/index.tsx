import React, { useState } from 'react'
import {Button, Modal} from 'antd'
import ShoppingCartOutlined from '@ant-design/icons/lib/icons/ShoppingCartOutlined'

import './styles.scss'


interface FloatingCartProps{
	title?: string
	limit: number
	count: number
	children: React.ReactNode
	disabled?: boolean
	loading?: boolean
	onSubmit: ()=> void
}

const FloatingCart:React.FC<FloatingCartProps> = ({
	title, count, limit, children, loading, disabled, onSubmit
})=>{

	const [open, setOpen] = useState<boolean>(false)
	const onClose = ()=>{
		if(loading) return
		setOpen(false)
	}
	
	return (
		<div className="FloatingCart">
			<p>{`${count}/${limit}`}</p>
			<Button shape="circle" size="large" type="primary" onClick={()=> setOpen(true)}>
				<ShoppingCartOutlined />
			</Button>
			<Modal title={title || 'Cart'} visible={open} onCancel={onClose} footer={
				<RenderFooter 
					onClose={onClose}
					loading={loading}
					disabled={disabled}
					onSubmit={onSubmit}
				/>
			}>
				{children}
			</Modal>
		</div>
	)
}


interface RenderFooterProps{
	onClose: ()=> void
	disabled?: boolean
	loading?: boolean
	onSubmit: ()=> void
}
const RenderFooter:React.FC<RenderFooterProps> = ({
	onClose, loading, disabled, onSubmit
})=>{
	return (
		<div className="FloatingCart__footer">
			<Button
				shape="round"
				disabled={disabled}
				loading={loading}
				type="primary"
				size="large"
				onClick={onSubmit}
			>
				Pick your meals
			</Button>
			<Button
				disabled={loading}
				shape="round"
				type="default"
				size="large"
				htmlType="button"
				onClick={onClose}
			>
				Continue Browsing
			</Button>
		</div>
	)
}

export default FloatingCart
