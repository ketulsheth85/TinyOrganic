import React,{useState} from 'react'

import TextInputWithButton from 'components/TextInputWithButton'
import { TinyP } from 'components/Typography'
import { Col, Row } from 'antd'
import { RenderInfoToast } from 'components/Toast'

interface DiscountCodeFormProps{
	onApplyDiscountCode: (code:string) => Promise<any>
	cta?: string
 }
const DiscountCodeForm:React.FC<DiscountCodeFormProps> = ({
	onApplyDiscountCode,
	cta="APPLY"
})=>{
	const [code, setCodeValue] = useState('')
	const [loading, setLoading] = useState(false)
	const submit = ()=>{
		if(code.length == 0){
			RenderInfoToast('Discount code field is required')
			return
		}
		setLoading(true)
		onApplyDiscountCode(code)
		.finally(()=>{
			setLoading(false)
		})
	}
	return (
		<Row className="margin-top-20">
			<Col span={24}>
				<TinyP 
					className={`
						font-16
						font-italic
						color-deep-ocean
						weight-600
						margin-top-20
						margin-right-20
						margin-right
					`}
				>
					Enter discount below to have applied on future orders. 
				</TinyP>
			</Col>
			<Col span={24} md={12}>
				<TextInputWithButton 
					onChange={(e:any)=> setCodeValue(e.target.value)}
					onSubmit={submit}
					disabledButton={loading}
					readonly={loading}
					value={code}
					cta={cta}
				/>
			</Col>
		</Row>
	)
}

export default DiscountCodeForm
