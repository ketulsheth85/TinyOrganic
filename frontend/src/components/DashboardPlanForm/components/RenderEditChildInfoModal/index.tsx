import React from 'react'

import { ChildrenType } from 'api/ChildrenAPI/types'
import TinyModal from 'src/shells/TinyModal'
import { ChildrenInformationForm } from 'components/ChildrenInfoForm/index.tsx'
import RenderEditInfoModalViewController from './vc'

interface RenderEditChildInfoModalProps{
	isModalVisible: boolean,
	onCloseModal: ()=> void
	currentChild: ChildrenType
	onSubmit: (allergies: Array<string>)=> void
}
const RenderEditChildInfoModal:React.FC<RenderEditChildInfoModalProps> = ({
	onCloseModal,
	isModalVisible,
	currentChild,
	onSubmit
})=>{

	const {
		fields: {
			loading,
		},
		actions,
	} = RenderEditInfoModalViewController(
		onSubmit,
	)

	return (
		<TinyModal
			title={`Editing ${currentChild.firstName}'s info`}
			isModalVisible={isModalVisible}
			closable={false}
		>
			<ChildrenInformationForm 
				onSubmit={actions.onSubmit}
				onBack={onCloseModal}
				currentChild={currentChild}
				onBackCta='Cancel'
				loading={loading}
			/>
		</TinyModal>
	)
}

export default RenderEditChildInfoModal
