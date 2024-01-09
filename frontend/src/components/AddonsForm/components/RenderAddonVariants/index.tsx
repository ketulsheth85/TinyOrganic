import React from 'react'
import {Form, Select} from 'antd'

import { ProductVariant } from 'api/ProductsAPI/types'

import './styles.scss'

interface RenderAddOnVariantsProps{
	variants: Array<ProductVariant>
	setVariant: (variant: ProductVariant) => void
}
const RenderAddOnVariants:React.FC<RenderAddOnVariantsProps> = ({variants, setVariant})=>{
	const OnSelectChange = (variantID: string) => {
		const variant = variants.find((variant) => variantID === variant.id)
		// added if statement to make typescript happy :)
		if(variant){
			setVariant(variant)
		}
	}
	return (
		<Form>
			<Form.Item style={{
				marginBottom: 10
			}}>
				<Select
					className="RenderAddOnVariants"
					placeholder='Choose an Option'
					defaultValue={variants[0].id}
					onChange={OnSelectChange}
				>
					{
						variants.map((variant)=>{
							if(variant.title){
								return (
									<Select.Option key={variant.id} value={variant.id}>
										{variant.title}
									</Select.Option>
								)
							}
							
						})
					}
				</Select>
			</Form.Item>
		</Form>
	)
}

export default RenderAddOnVariants
