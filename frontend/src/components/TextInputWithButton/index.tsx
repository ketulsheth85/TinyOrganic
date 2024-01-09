import React from 'react'

import './styles.scss'


export interface TextInputWithButtonProps{
	cta?: string
	onChange?: (e:any) => void
	onClick?: (e:any) => void
	onClickElement?: (e?:React.ChangeEvent<HTMLInputElement>) => void
	onSubmit?: (e?:React.ChangeEvent<HTMLInputElement>) => void 
	placeholder?: string
	value?: string
	disabledButton?: boolean
	readonly?:boolean
}

const TextInputWithButton:React.FC<TextInputWithButtonProps> = ({
	cta,
	placeholder,
	onSubmit,
	disabledButton,
	onClickElement,
	...rest
})=>{
	const _onSubmit = ()=>{
		onSubmit && onSubmit()
	}
	const _onClickElement = ()=>{
		onClickElement && onClickElement()
	}
	return (
		<div className="TextInputWithButton" onClick={_onClickElement}>
			<input
				type="text" 
				placeholder={placeholder || ''}
				{...rest}
			/>
			<button disabled={disabledButton} onClick={_onSubmit}>{cta || 'Submit'}</button>
		</div>
	)
}

export default TextInputWithButton
