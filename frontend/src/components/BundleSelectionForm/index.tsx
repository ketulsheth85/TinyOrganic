import React, { Fragment, useEffect, useState } from 'react'
import { 
	Col,
	Form,
	Select,
	Button,
} from 'antd'
import { get } from 'lodash'
import { isRejectedWithValue } from '@reduxjs/toolkit'
import { useDispatch, useSelector } from 'react-redux'

import FormWrapper,{
	ButtonContainer
} from 'src/shells/FormWrapper'
import { ChildrenType } from 'api/ChildrenAPI/types'
import { createSubscription, SubscriptionSliceState, updateCustomer } from 'store/subscriptionSlice'
import { MultipageFormComponentProps } from 'src/shells/MultiPageForm'
import {  AppDispatch, RootState } from 'store/store'
import { CreateCustomerSubscriptionPayload } from 'api/SubscriptionAPI/types'
import BundleSelectionCard from 'components/BundleSelectionCard'
import { SplashPage } from 'components/OnboardingSplashPage'
import { RenderErrorPage } from 'src/shells/ErrorBoundary'

import './styles.scss'
import analyticsClient from 'src/libs/analytics'


export interface BundleSelectionFormProps{
	store: SubscriptionSliceState
	currentChild: ChildrenType,
	onSubmit: (payload: CreateCustomerSubscriptionPayload)=>void,
	onBack?: ()=> void
}

export const BundleSelectionForm:React.FC<BundleSelectionFormProps> = ({
	store,
	currentChild,
	onSubmit,
	onBack,
}) =>{

	useEffect(()=>{
		analyticsClient.pageView('Onboarding', 'Plan Selection', {
			first_name: store.firstName,
			last_name: store.lastName,
			email: store.email,
			child: currentChild
		})
	}, [])

	const {
		APIStatus,
		subscriptions
	} = store

	const [numberOfServings, setNumberOfServings] = 
	useState<number>(get(subscriptions, `[${currentChild.id}].numberOfServings`, 24) as number)
	const [frequency, setFrequency] = 
	useState<number>(get(subscriptions, `[${currentChild.id}].frequency`, 2) as number)

	const _onSubmit = ()=>{
		if((window as any).analytics){
			(window as any).analytics.track('Selected Plan', {
				customer_id: store.id,
				customer_child: currentChild.id,
				email: store.email,
				first_name: store.firstName,
				last_name: store.lastName,
			})
		}
		onSubmit({
			frequency,
			numberOfServings,
			customer: store.id,
			customerChild: currentChild.id
		})
	}

	const _onBack = () =>{
		if(onBack){
			onBack()
		}
	}

	return (
		<div className="BundleSelectionForm">
			<FormWrapper
				title={`Choose ${currentChild.firstName}'s Meal Plan`}
				subtitle="You can adjust your plan preferences at any time!"
				className="OnboardingPageOverrides"
			>
				<div className="BundleSelectionForm__body">
					<div className="BundleSelectionForm__cards">
						<BundleSelectionCard 
							title="12"
							subheader="meals"
							text="Pay $5.49 per meal"
							active={numberOfServings === 12}
							onClick={()=> setNumberOfServings(12)}
						/>
						<BundleSelectionCard 
							featuredText="Best Value"
							title="24"
							subheader="meals"
							text="Starting at $4.66 per meal"
							active={numberOfServings === 24}
							onClick={()=> setNumberOfServings(24)}
						/>
					</div>
					<div>
						<Form.Item
							name="frequency"
							rules={[{ required: true, message: 'This field is required' }]}
							initialValue={frequency}
						>	
							<p className="BundleSelectionForm__label">every</p>
							<Select
								value={frequency as number}
								placeholder="Select Delivery frequency"
								onChange={(value:number)=>{
									setFrequency(value)
								}}
							>
								<Select.Option value={1}>1 weeks</Select.Option>
								<Select.Option value={2}>2 weeks</Select.Option>
								<Select.Option value={4}>4 weeks</Select.Option>
							</Select>
						</Form.Item>
					</div>
					<Col span={24}>
						<ButtonContainer unstickyOnMobile>
							<>
								<p className="ButtonContainer__remark">
									{numberOfServings === 24 ? 
										'You\'re saving $20 per delivery' :
										'You could be saving $20 per delivery by choosing 24 meals'}
								</p>
								<Button
									className="margin-bottom-20"
									onClick={_onSubmit}
									loading={APIStatus === 'loading'}
									type="primary"
									size="large"
									htmlType="submit"
								>
									Pick your meals
								</Button>
								{
									onBack && (
										<Button
											type="default"
											size="large"
											htmlType="button"
											onClick={_onBack}
										>
										Back
										</Button>
									)
								}
							</>
						</ButtonContainer>
					</Col>
				</div>
			</FormWrapper>
		</div>
	)
}




const BundleSelectionFormHOC:React.FC<MultipageFormComponentProps> = ({
	shouldSeeQuestion,
	onBack,
	onSubmit
}) =>{
	const [shouldRenderQuestion, setShouldRenderPage] = useState(false)
	const [error, setError] = useState('')
	const [state,setState] = useState({
		cursor: 0,
	})

	const dispatch = useDispatch<AppDispatch>()
	const store = useSelector((state:RootState)=> state.subscription)

	/**
	 * initialize page
	 */
	const init = async ()=>{
		const _shouldRenderQuestion = shouldSeeQuestion(`
		It looks like you haven't gotten to the "Bundle Selection" just yet,
		please fill out the form below to continue 😊
	`)
		if(_shouldRenderQuestion){
			setShouldRenderPage(_shouldRenderQuestion)
		}
	}

	useEffect(()=>{
		init()
	}, [])

	const _onSubmit = (payload: CreateCustomerSubscriptionPayload)=>{
		const shouldLoop =  state.cursor + 1 < store.children.length
		dispatch(createSubscription(payload))
			.then((action)=>{
				if(isRejectedWithValue(action)) return
				if(shouldLoop){
					setState(({cursor})=>{
						return {
							cursor: cursor+1
						}
					})
				}
				else{
					onSubmit()
				}
			})
	}

	const _onBack= (shouldLoop?:boolean)=>{
		const _shouldLoop = state.cursor > 0
		if(_shouldLoop){
			setState(({cursor})=>{
				return {
					cursor: cursor-1
				}
			})
		}
		else if(onBack){
			onBack(shouldLoop)
		}
	}

	if(!shouldRenderQuestion){
		return (
			<SplashPage />
		)
	}

	if(error){
		return (
			<RenderErrorPage message={error} />
		)
	}

	return (
		<>
			{store.children.map((child: ChildrenType, i:number)=>{
				return (
					<Fragment key={child.firstName}>
						{
							state.cursor === i && (
								<BundleSelectionForm
									store={store}
									onSubmit={_onSubmit}
									currentChild={child}
									onBack={onBack && _onBack}
								/>
							)
						}
					</Fragment>
				)
			})}
		</>
	)
}
export default BundleSelectionFormHOC
