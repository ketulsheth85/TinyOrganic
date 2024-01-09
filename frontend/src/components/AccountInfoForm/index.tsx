import React, {useEffect, useState} from 'react'

import { 
	Col,
	Form,
	Input,
	Button,
	Row
} from 'antd'
import { useDispatch, useSelector } from 'react-redux'
import {isRejectedWithValue} from '@reduxjs/toolkit'

import {resetStore} from 'src/store/cartSlice'
import { AppDispatch  } from 'store/store'
import {addCustomerAddress, createConsumer, initOnboarding, updateCustomer, updateCustomerAddress} from 'store/subscriptionSlice'
import FormWrapper,{
	ButtonContainer
} from 'src/shells/FormWrapper'
import {
	EMAIL_REGEX, ZIP_CODE_REGEX,
} from 'src/utils/constants'
import { MultipageFormComponentProps } from 'src/shells/MultiPageForm'
import { CustomerCreationPayload } from 'api/CustomerAPI/types'
import { RootState } from 'store/store'
import AdjacentFormField from 'src/shells/AdjacentFormField'
import { Hx, TinyP } from 'components/Typography'
import { DownFacingTriangle, VegetableIcon } from 'components/svg'
import analyticsClient from 'src/libs/analytics'
import {SplashPage} from 'components/OnboardingSplashPage'

import './styles.scss'
import { CustomerSubscriptionCreationResponse } from 'api/SubscriptionAPI/types'

const AccountInformationForm:React.FC<MultipageFormComponentProps> = ({
	onSubmit,
	onBack
})=>{
	
	const dispatch = useDispatch<AppDispatch>()
	const subscription = useSelector((state: RootState) => state.subscription)
	const {
		APIStatus,
		firstName,
		lastName,
		email,
		addresses
	} = subscription

	const [loading, setLoading] = useState(true)
	const getZipcode = ()=> addresses.length > 0 ? addresses[0].zipcode : undefined
	const shouldCreateNewAddress = (createdCustomer:CustomerSubscriptionCreationResponse)=>{
		return createdCustomer.isNew || createdCustomer.addresses.length === 0
	}

	useEffect(()=>{
		dispatch(initOnboarding())
			.finally(()=>{
				setLoading(false)
			})
	},[])

	const _onSubmit = async (payload:CustomerCreationPayload)=>{
		const createCustomerAction = await dispatch(createConsumer(payload))
		if(isRejectedWithValue(createCustomerAction)) return
		const updatedCustomer = (createCustomerAction.payload as CustomerSubscriptionCreationResponse)
		let addressAction
		if(shouldCreateNewAddress(updatedCustomer)){
			addressAction = await dispatch(addCustomerAddress({
				customer: updatedCustomer.id,
				firstName: updatedCustomer.firstName,
				lastName: updatedCustomer.lastName,
				email: updatedCustomer.email,
				zipcode: payload.zipcode
			}))
		}
		else{
			addressAction = await dispatch(updateCustomerAddress({
				id: addresses[0].id,
				customer: updatedCustomer.id,
				firstName: updatedCustomer.firstName,
				lastName: updatedCustomer.lastName,
				email: updatedCustomer.email,
				zipcode: payload.zipcode,
				partial: true
			}))
		}
		if(isRejectedWithValue(addressAction	)) return
		dispatch(resetStore());
		/**
		 * We call window object directly as we've had issues
		 * with other scripts in the past when adding adapters
		 */
		(window as any).liQ = (window as any).liQ || [];
		(window as any).liQ.push({
			'event': 'conversion',
			'name': 'email_signup',
			'email': payload.email
		})
		onSubmit()
	}

	const _onBack = ()=>{
		if(onBack){
			onBack()
		}
	}


	useEffect(()=>{
		analyticsClient.pageView('Onboarding', 'Sign Up')
	},[])
  
	if(loading){
		return (
			<SplashPage />
		)
	}

	return (
		<>
			<RenderHeader />
			<FormWrapper
				tagline="First, tell us a little about yourself:"
				className={`
				AccountInfoForm
				OnboardingPageOverrides
				margin-x-auto
				max-width-500
				padding-bottom-100
			`}
			>
				<Col span={24}>
					<Form
						name="basic"
						layout="vertical"
						wrapperCol={{ span: 24 }}
						autoComplete="off"
						validateTrigger="onBlur"
						onFinish={_onSubmit}
						initialValues={{
							firstName,
							lastName,
							email,
							zipcode: getZipcode()
						}}
					>
						<Row>
							<Col className="typography text-center" span={24}>
								<TinyP
									className={`
									color-deep-ocean
									font-supria-sans
									font-16
									weight-300
									font-24
								`}
									marginBottom={4}
								>
								My name is	
								</TinyP>
								<AdjacentFormField>
									<Form.Item
										name="firstName"
										rules={[
											{ required: true, message: 'First name is a required field' },
										]}
									>
										<Input 
											placeholder="First Name"
										/>
									</Form.Item>
								</AdjacentFormField>
							</Col>
							<Col span={24}>
								<AdjacentFormField className="margin-bottom-12">
									<Form.Item
										name="lastName"
										rules={[
											{ required: true, message: 'Last name is a required field' },
										]}
									>
										<Input 
											placeholder="Last Name"
										/>
									</Form.Item>
								</AdjacentFormField>
							</Col>
							<Col span={24} className="typography text-center">
								<TinyP
									className={`
									color-deep-ocean
									font-supria-sans
									font-16
									weight-300
									font-24
								`}
									marginBottom={4}
								>
								My email is
								</TinyP>
								<AdjacentFormField>
									<Form.Item
										name="email"
										rules={[
											{ required: true, message: 'Email is required field' },
											{ pattern: EMAIL_REGEX, message: 'Email must be valid format'}
										]}
									>
										<Input 
											placeholder="Email Address"
										/>
									</Form.Item>
								</AdjacentFormField>
							</Col>
							<Col span={24} className="typography text-center">
								<TinyP
									className={`
									color-deep-ocean
									font-supria-sans
									font-16
									weight-300
									font-24
								`}
									marginBottom={4}
								>
								My zip code is
								</TinyP>
								<AdjacentFormField>
									<Form.Item
										name="zipcode"
										rules={[
											{ required: true, message: 'Zip code is required field' },
											{ pattern: ZIP_CODE_REGEX, message: 'Zip code only contain 5 numbers. No spaces, or letters allowed'}
										]}
									>
										<Input 
											placeholder="Zip code"
										/>
									</Form.Item>
								</AdjacentFormField>
							</Col>
						</Row>
						<ButtonContainer unstickyOnMobile>
							<>
								<Button
									type="primary"
									size="large"
									htmlType="submit"
									loading={APIStatus === 'loading'}
								>
								Continue
								</Button>
								{onBack && (
									<Button
										type="default"
										size="large"
										htmlType="button"
										onClick={_onBack}
									>
								Back
									</Button>
								)}
							</>
						</ButtonContainer>
					</Form>
				</Col>
			</FormWrapper>
		</>
	)
}


const RenderHeader = ()=>{
	return (
		<div className={`
			-margin-top-20
			-margin-x-20
			margin-bottom-40
			position-relative
			background-pink-dark
			flex
			padding-top-14
			padding-x-24
			padding-bottom-60
		`}>
			<div className={`
				max-width-500
				margin-auto
				typography
				text-center
				color-white
			`}>
				<VegetableIcon 
					fill="#FAE46F"
					height={50}
					width={50}
				/>
				<Hx
					tag="h3"
					className={`
						font-36
						color-white
						weight-600
					`}
				>
					Let&apos;s build your little one&apos;s
					personalized menu
				</Hx>
				<TinyP
					className={`
						color-white
						font-14
					`}
					lineHeight={5}	
				>
				Get your little one’s recommended recipes and
				choose your plan preferences, all in under 2 minutes!
				</TinyP>
			</div>
			<div
				style={{
					position: 'absolute',
					bottom: -15,
					left: '50%',
					transform: 'translateX(-50%)',
				}}
			><DownFacingTriangle /></div>
		</div>
	)
}

export default AccountInformationForm
