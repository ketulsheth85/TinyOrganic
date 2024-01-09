import React from 'react'
import { 
	Col,
	Form,
	Input,
	Button,
	Row,
} from 'antd'
import { useDispatch } from 'react-redux'
import { isRejectedWithValue } from '@reduxjs/toolkit'
import cx from 'classnames'

import {
	AddCustomerDetails, updateCustomer
} from 'src/store/subscriptionSlice'
import FormWrapper,{
	ButtonContainer
} from 'src/shells/FormWrapper'
import { MultipageFormComponentProps } from 'src/shells/MultiPageForm'
import { EMAIL_REGEX, NO_SPACE_REGEX, PHONE_NUMBER_REGEX } from 'src/utils/constants'
import { AppDispatch } from 'store/store'
import { AddCustomerDetailsPayload } from 'api/CustomerAPI/types'
import { omit } from 'lodash'



export interface AccountDetailsFormProps extends MultipageFormComponentProps{
	className?: string
	passwordEditable?: boolean
}

const AccountDetailsForm:React.FC<AccountDetailsFormProps> = ({
	className,
	onSubmit,
	onBack,
	passwordEditable,
	store,
	
})=>{
	const dispatch = useDispatch<AppDispatch>()
	const {
		firstName,
		lastName,
		email,
		phoneNumber,
		id,
		APIStatus,
	} = store

	const _onSubmit = (payload:AddCustomerDetailsPayload)=>{
		payload.id = id
		const _payload = omit(payload, ['confirm'])
		if(passwordEditable){
			dispatch(AddCustomerDetails(_payload as AddCustomerDetailsPayload))
				.then((action)=>{
					if(!isRejectedWithValue(action)) onSubmit()
				})
		}
		else{
			const _payload = omit(payload, ['password'])
			dispatch(updateCustomer(_payload))
				.then((action)=>{
					if(!isRejectedWithValue(action)) onSubmit()
				})
		}
	}

	const _onBack = ()=>{
		if(onBack){
			onBack()
		}
	}

	const classes = cx('',{
		[`${className}`]: !!className
	})

	return (
		<FormWrapper className={classes}>
			<Col span={24}>
				<Form
					name="AccountDetailsForm"
					layout="vertical"
					initialValues={{
						firstName,
						lastName,
						email,
						phoneNumber,
					}}
					wrapperCol={{ span: 24 }}
					autoComplete="off"
					validateTrigger="onBlur"
					onFinish={_onSubmit}
				>
					<Row gutter={16}>
						<Col span={24}  md={12}>
							<Form.Item
								label="First Name"
								name="firstName"
								rules={[
									{ required: true, message: 'First name is a required field' },
								]}
							>
								<Input 
									placeholder="Bob"
								/>
							</Form.Item>
						</Col>
						<Col span={24}  md={12}>
							<Form.Item
								label="Last Name"
								name="lastName"
								rules={[
									{ required: true, message: 'Last name is a required field' },
								]}
							>
								<Input 
									placeholder="Tiny"
								/>
							</Form.Item>
						</Col>
						<Col span={24} md={12}>
							<Form.Item
								label="Email"
								name="email"
								rules={[
									{ required: true, message: 'Email is a required field' },
									{ pattern: EMAIL_REGEX, message: 'Email must be valid format'}
								]}
							>
								<Input 
									placeholder="Tiny"
								/>
							</Form.Item>
						</Col>
						<Col span={24} md={12}>
							<Form.Item
								label="Phone Number"
								name="phoneNumber"
								rules={[
									{ required: true, message: 'Phone Number is a required field' },
									{ pattern: PHONE_NUMBER_REGEX, message: 'Email must be of the format DDD DDD DDDD'}
								]}
							>
								<Input 
									placeholder="123 123 1234"
								/>
							</Form.Item>
						</Col>
						{passwordEditable && (
							<>
								<Col span={24} md={12}>
									<Form.Item
										name="password"
										label="Password"
										rules={[
											{required: true, message: 'Password is required'},
											{ min: 5, message: 'Password must be at least 5 characters' },
											{pattern: NO_SPACE_REGEX, message: 'No spaces allowed in the password field'}
										]}
										hasFeedback
									>
										<Input.Password />
									</Form.Item>
								</Col>
								<Col span={24} md={12}>
									<Form.Item
										name="confirm"
										label="Confirm Password"
										dependencies={['password']}
										hasFeedback
										rules={[
											{ required: true, message: 'Please confirm your password!',},
											({ getFieldValue }) => ({
												validator(_, value) {
													if (!value || getFieldValue('password') === value) {
														return Promise.resolve()
													}
													return Promise.reject(new Error('The two passwords that you entered do not match!'))
												},
											}),
										]}
									>
										<Input.Password />
									</Form.Item>
								</Col>
							</>
						)}
					</Row>
					<ButtonContainer
						unstickyOnMobile
					>
						<>
							<Button
								type="primary"
								size="large"
								htmlType="submit"
								loading={APIStatus === 'loading'}
							>
								Submit
							</Button>
							{onBack && (
								<Button
									type="default"
									size="large"
									htmlType="button"
									onClick={_onBack}
								>
								Cancel
								</Button>
							)}
						</>
					</ButtonContainer>
				</Form>
			</Col>
		</FormWrapper>
	)
}

export default AccountDetailsForm
