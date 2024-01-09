import React from 'react'
import { Modal } from 'antd'

interface RenderModal{
	title?: string
	isModalVisible: boolean
	children?: React.ReactNode
}
const RenderModal:React.FC<RenderModal> = ({
	title,
	isModalVisible,
	children
})=>{
	return (
		<>
			<Modal
				className="AddonsForm__modal"
				title={title}
				visible={isModalVisible} 
				footer={null}
				closable={false}
			>
				{children}
			</Modal>
		</>
	)
}

export default RenderModal
