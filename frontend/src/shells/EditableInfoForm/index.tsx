import React from 'react'
import {Card} from 'antd'
import cx from 'classnames'

import { Caret } from 'src/components/svg'

import './styles.scss'

export interface EditableInfoFormProps{
	title: string
	open: boolean
	isEditable?: boolean
	setOpen?: (value: boolean)=>void
	details?: Array<string | number>
	children: React.ReactNode
}

const EditableInfoForm:React.FC<EditableInfoFormProps> = ({
	title,
	open,
	setOpen,
	children,
})=>{

	const _setOpen = ()=> {
		if(!setOpen) return
		setOpen(!open)
	}

	const classes = cx('EditableInfoForm', {
		'EditableInfoForm--open': open
	})

	const caretClasses = cx('EditableInfoForm__caret', {
		'EditableInfoForm__caret--open': open
	})

	return (
		<div className={classes}>
			<div className="EditableInfoForm__header">
				<h3>{title}</h3>
				{setOpen && (
					<span className={caretClasses} onClick={_setOpen}>
						<Caret height={12} width={14}/>
					</span>
				)}
			</div>
			{open && children}
		</div>
	)
}


export interface EditableInfoFormCardProps extends EditableInfoFormProps{
	// optional child component that replaces button
	ChildComponent?: React.FC,
	onEditButtonCTA?: string
}

export const EditableInfoFormCard:React.FC<EditableInfoFormCardProps> = ({
	title,
	open,
	details,
	setOpen,
	children,
	ChildComponent,
	isEditable = true,
	onEditButtonCTA = 'Edit',
})=>{

	const _setOpen = ()=> {
		if(!setOpen) return
		setOpen(!open)
	}

	const classes = cx('EditableInfoForm EditableInfoFormCard', {
		'EditableInfoForm--open': open
	})
	return (
		<Card className={classes}>
			<div className="EditableInfoForm__header">
				<h3>{title}</h3>
				{
					!ChildComponent && isEditable &&(
						<button onClick={_setOpen} className="EditableInfoForm__open-btn">
							{!open ? (
								<div> {onEditButtonCTA} </div>
							) : <div> Cancel </div>}
						</button>
					)
				}
				{
					ChildComponent && (
						<ChildComponent />
					)
				}
			</div>
			{open && children}
			{!open && details && <RenderDetails details={details} />}
		</Card>
	)
}


export default EditableInfoForm

export interface RenderDetailsProps{
	details: Array<string | number>
}

export const RenderDetails:React.FC<RenderDetailsProps> = ({
	details
}) =>{
	if(details.length === 0){
		return <p className="EditableInfoForm__details">No information available</p>
	}
	return(
		<div>
			{details.map((value, i)=> <p className="EditableInfoForm__details" key={`${value}-${i}`}>{value}</p>)}
		</div>
	)
}

export interface EditableInfoFormButtonSchema{
	text: string
	onClick: ()=> void
}
export interface EditableInfoFosrmButtonsProps{
	buttons: Array<EditableInfoFormButtonSchema>
}
export const EditableInfoFormButtons:React.FC = ()=> {
	return(
		<div>
			Editable info form
		</div>
	)
} 
