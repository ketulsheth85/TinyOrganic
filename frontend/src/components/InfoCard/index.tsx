import { QuestionMarkIconFilled } from 'components/svg'
import { Hx, TinyP } from 'components/Typography'
import React from 'react'

export interface InfoCardProps{
	title?: string
	text?: string
}
const InfoCard:React.FC<InfoCardProps> = ({
	title,
	text
})=>{
	return (
		<div className={`
			flex
			align-center
			background-beige-medium
			padding-20			
		`}>
			<div className="margin-right-24">
				<QuestionMarkIconFilled />
			</div>
			<div>
				{title && (
					<Hx 
						tag="h5"
						className={`
						font-supria-sans
						font-italic
						weight-600
						font-16
						color-brown-dark
					`}
						marginBottom={3}
					>
						{title}
					</Hx>
				)}
				{text && (
					<TinyP
						className={`
							font-supria-sans
							weight-300
							font-16
							color-brown-dark
						`}
					>
						{text}
					</TinyP>
				)}
			</div>
		</div>
	)
}

export default InfoCard
