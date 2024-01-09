import React, { useState } from 'react'
import { 
	Col,
	Form,
	Input,
	Button,
	Row,
	Select
} from 'antd'
import { useDispatch } from 'react-redux'
import { isRejectedWithValue } from '@reduxjs/toolkit'
import { omit } from 'lodash'

import {
	addCustomerAddress,
	updateCustomerAddress
} from 'src/store/subscriptionSlice'
import FormWrapper,{
	ButtonContainer
} from 'src/shells/FormWrapper'
import {
	NO_PO_BOX_REGEX,
} from 'src/utils/constants'
import { MultipageFormComponentProps } from 'src/shells/MultiPageForm'
import { CustomerAddress, CustomerAddressCreationPayload, CustomerAddressUpdatePayload } from 'api/AddressAPI/types'
import { STATES_HASH } from 'src/utils/constants'
import { ZIP_CODE_REGEX } from 'src/utils/constants'
import { AppDispatch } from 'store/store'
import { TinyP } from 'components/Typography'
import TinyModal, { TinyModalProps } from 'src/shells/TinyModal'

const AddressInfoForm:React.FC<MultipageFormComponentProps> = ({
	onSubmit,
	onBack,
	store
})=>{
	
	const dispatch = useDispatch<AppDispatch>()
	const {
		addresses,
		id,
		APIStatus,
		firstName,
		lastName,
		email
	} = store

	const [invalidAddressMessages, setInvalidAddressMessages] = useState<Array<string>>([])
	const [renderAddressDisclosure, setRenderAddressDisclosure] = useState(false)
	const [submittedAddress, setSubmitttedAddress] = useState<CustomerAddress>()

	const resolveAddressResponse = (customerAddress:CustomerAddress, validation=true)=>{
		if(validation && customerAddress.messages && customerAddress.messages.length){
			setInvalidAddressMessages(customerAddress.messages || [])
			setRenderAddressDisclosure(true)
		}
		else{
			onSubmit()
		}
	}


	const _onSubmit = (payload:Partial<CustomerAddress>, validation=true)=>{
		payload.customer = id
		const _payload = {
			...payload,
			firstName,
			lastName,
			email
		} as CustomerAddressUpdatePayload
		setInvalidAddressMessages([])
		setSubmitttedAddress(payload as CustomerAddress)
		/**
		 * only allow customer to add one address until
		 * we add multi address support
		 **/
		if(addresses.length > 0){
			_payload.id = addresses[0].id
			dispatch(updateCustomerAddress(_payload))
				.then((action)=>{
					if(!isRejectedWithValue(action)){
						resolveAddressResponse(action.payload as CustomerAddress,validation)
					} 
				})
		}
		else{
			dispatch(addCustomerAddress(_payload))
				.then((action)=>{
					if(!isRejectedWithValue(action)){
						resolveAddressResponse(action.payload as CustomerAddress,validation)
					}
				})
		}
	}

	const _onBack = ()=>{
		if(onBack){
			onBack()
		}
	}

	return (
		<FormWrapper className="OnboardingPageOverrides">
			<Col span={24}>
				<Form
					name="basic"
					layout="vertical"
					initialValues={addresses.length > 0 ? addresses[0] : {}}
					wrapperCol={{ span: 24 }}
					autoComplete="off"
					validateTrigger="onBlur"
					onFinish={_onSubmit}
				>
					<Row gutter={16}>
						<Col span={24} md={12}>
							<Form.Item
								label="Address"
								name="streetAddress"
								rules={[
									{ required: true, message: 'Address is a required field' },
									{ pattern: NO_PO_BOX_REGEX, message: 'Sorry no PO BOX address 🚫  📪'}
								]}
							>
								<Input 
									placeholder="12345 SW 67 ST"
								/>
							</Form.Item>
						</Col>
						<Col span={24} md={12}>
							<Form.Item
								label="City"
								name="city"
								rules={[
									{ required: true, message: 'City is a required field' },
								]}
							>
								<Input 
									placeholder="New York"
								/>
							</Form.Item>
						</Col>
						<Col span={24} md={12}>
							<Form.Item
								label="State"
								name="state"
								rules={[{ required: true, message: 'State is a field is required' }]}
							>
								<Select
									showSearch
									className="HouseHoldInfoForm__input__field"
									placeholder='Select an Option'
									optionFilterProp='children'
								>
									{Object.keys(STATES_HASH).map((name)=>(
										<Select.Option key={name} value={STATES_HASH[name]}>{name}</Select.Option>
									))}	
								</Select>

							</Form.Item>
						</Col>
						<Col span={24} md={12}>
							<Form.Item
								label="Zip Code"
								name="zipcode"
								rules={[
									{ required: true, message: 'Zip code is a required field' },
									{ pattern: ZIP_CODE_REGEX, message: 'Zip code must contain five digits (no letters or special characters)'}
								]}
							>
								<Input
									placeholder="12345"
								/>
							</Form.Item>
						</Col>
						<RenderInvalidAddressDisclosure 
							address={submittedAddress}
							isModalVisible={renderAddressDisclosure}
							messages={invalidAddressMessages}
							onCancel={()=> setRenderAddressDisclosure(false)}
							onSubmit={()=> onSubmit()}
						/>
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

export default AddressInfoForm

interface RenderInvalidAddressDisclosureProps extends TinyModalProps{
	address?: CustomerAddress
	messages: Array<string>
	onSubmit: ()=> void
	onCancel: ()=> void
}
const RenderInvalidAddressDisclosure:React.FC<RenderInvalidAddressDisclosureProps> = ({
	address,
	messages,
	onSubmit,
	onCancel,
	isModalVisible,
})=>{
	return (
		<TinyModal title="Something went wrong while adding your address" isModalVisible={isModalVisible} closable={false}>
			{address && (
				<TinyP className="font-16 text-center font-300" lineHeight={6}>
					Address entered: <br/>
					<strong>{`${address.streetAddress}, ${address.city} ${address.state} ${address.zipcode}`}</strong>
				</TinyP>
			)}
			<TinyP className='font-16'>
				The following errors occurred while adding your address. 
			</TinyP>
			<ul className="margin-bottom-12">
				{
					messages.map((message)=>{
						return (
							<li style={{color: 'red'}} key={message} >{message}</li>
						)
					})
				}
			</ul>
			<TinyP className="font-16">
				Please ensure that the <strong>address</strong> provided is <strong>complete</strong> and
				<strong> correct</strong>. If you believe the address is correct, you can continue.
			</TinyP>
			<div className="padding-top-20">
				<Button 
					className="margin-right-8"
					shape="round" 
					onClick={onCancel} 
					type="primary">
						Update Address
				</Button>
				<Button
					className="padding-0" 
					shape="round"
					onClick={onSubmit} 
					type="default" 
					size="small">
						Continue with current address
				</Button>
			</div>
		</TinyModal>
	)
}
