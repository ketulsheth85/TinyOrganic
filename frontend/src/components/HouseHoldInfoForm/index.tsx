import React, { useEffect, useState } from 'react'
import { 
	Col,
	Row,
	Form,
	Input,
	Select,
	Button
} from 'antd'
import cx from 'classnames'
import { useDispatch, useSelector } from 'react-redux'
import { isRejectedWithValue } from '@reduxjs/toolkit'

import { 
	AppDispatch,
	RootState
} from 'store/store'
import { addHouseHoldInfomation } from 'store/subscriptionSlice'
import { Customer } from 'api/CustomerAPI/types'
import { ChildrenType } from 'api/ChildrenAPI/types'
import { MultipageFormComponentProps } from 'src/shells/MultiPageForm'
import FormWrapper,{ButtonContainer} from 'src/shells/FormWrapper'
import { deepClone } from 'src/utils/utils'
import { omit } from 'lodash'
import AdjacentFormField from 'src/shells/AdjacentFormField'

import './styles.scss'
import { TinyP } from 'components/Typography'
import InfoCard from 'components/InfoCard'
import analyticsClient from 'src/libs/analytics'

/**
 * This component assumes that the subscription store has loaded
 * correctly
 */
const HouseHoldInfoForm:React.FC<MultipageFormComponentProps> = ({
	onSubmit,
	onBack
})=>{

	const dispatch = useDispatch<AppDispatch>()

	const { 
		id, // parentID,
		APIStatus,
		firstName,
		lastName,
		email,
		children,
	} = useSelector((state: RootState) => state.subscription)

	useEffect(()=>{
		analyticsClient.pageView('Onboarding', 'Household Info', {
			first_name:firstName,
			last_name: lastName,
			email: email,
		})
	},[])

	const defaultChildren:Array<ChildrenType> = [
		{
			id: '',
			firstName: '',
			birthDate: '',
			parent: '',
			sex: '',
			allergies: []
		}
	]

	const _children = children.length > 0? children : defaultChildren
	const [state, setState] = useState({
		childrenArr: _children,
		childCount: _children.length,
		submitted: false
	})

	const _onSubmit = ({guardianType}:Pick<Customer, 'guardianType'>)=>{
		if( (window as any).analytics){
			(window as any).analytics.identify(id, {
				first_name:firstName,
				last_name: lastName,
				email: email,
			})	
		}

		const {childrenArr, childCount} = state
		setState((state)=>({
			...state,
			submitted: true
		}))

		/**
		 * ant design does not validate dynamic fields
		 * so we have to do it manually
		 **/ 
		const childNameCount =
			childrenArr
				.slice(0,childCount)
				.reduce((acc:number, {firstName}: ChildrenType)=>{
					return firstName ? acc + 1 : acc
				}, 0)
		
		// do not submit if I am missing children names
		if(childNameCount < childCount){
			return
		}

		const _chidlren = childrenArr
			.slice(0,childCount).map((child)=>{
				return omit(child, ['allergies'])
			})

		dispatch(addHouseHoldInfomation({
			children: _chidlren,
			parentID: id,
			guardianType
		}))
			.then((action)=> {
				if(!isRejectedWithValue(action)) onSubmit()
			})
	}	

	const _onBack = ()=>{
		if(onBack){
			onBack()
		}
	}

	const onSelectChidlrenCount = (count:number)=>{
		setState((state)=>{
			const arr = [...state.childrenArr]
			while(arr.length < count){
				arr.push({
					id: '',
					firstName: '',
					birthDate: '',
					parent: '',
					sex: '',
					allergies: []
				})
			}
			const newState = {
				...state,
				childrenArr: arr,
				childCount: count
			}
			return newState
		})
	}

	const onChangeChildName = (idx:number) => (e:any) =>{
		const newName = e.currentTarget.value
		const childrenArr = deepClone(state.childrenArr)
		childrenArr[idx].firstName = newName
		setState((state)=>(
			{
				...state,
				childrenArr
			}
		))
		return
	}

	const childInputClasses = (hasError:boolean) =>{
		return cx('',{
			'HouseHoldInfoForm__input__field--error': hasError
		})
	}

	return (
		<FormWrapper
			tagline={`Nice to meet you ${firstName}!`}
			title="We need a little more info to customize your plan"
			subtitle="
			This helps us make sure we’re 
			recommending the best possible meal plan for you and your little ones.
			"
			className={`
				HouseholdInfoForm
				max-width-500
				margin-x-auto
				OnboardingPageOverrides
				padding-bottom-100
			`}
		>
			<Row className="HouseHoldInfoForm__form-outer">
				<Col span={24}>
					<Form
						name="household-info"
						autoComplete="off"
						validateTrigger="onBlur"
						onFinish={_onSubmit}
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
									I have
								</TinyP>
								<Form.Item
									wrapperCol={{span: 24}}
									name="childCount"
									rules={[{ required: true, message: 'This field is required' }]}
									initialValue={state.childCount}
								>
									<Select
										value={state.childCount}
										placeholder="Select an Option"
										onChange={onSelectChidlrenCount}
									>
										<Select.Option value={1}>one child</Select.Option>
										<Select.Option value={2}>two children</Select.Option>
										<Select.Option value={3}>three children</Select.Option>
									</Select>
								</Form.Item>
							</Col>
							<RenderChildrenField 
								{...state}
								onChangeChildName={onChangeChildName}
								childInputClasses={childInputClasses}
							/>
						</Row>
						<ButtonContainer unstickyOnMobile>
							<>
								<Button
									loading={APIStatus === 'loading'}
									type="primary"
									size="large"
									htmlType="submit"
								>
									CONTINUE
								</Button>
								{
									onBack && (
										<Button
											type="default"
											size="large"
											htmlType="button"
											onClick={_onBack}
										>
											BACK
										</Button>
									)
								}
							</>
						</ButtonContainer>
					</Form>
				</Col>
			</Row>
			<InfoCard 
				title="Why do we ask this:"
				text="
				Knowing more about you and your little ones 
				helps us recommend the right meal plan and recipes for your needs!
				"
			/>
		</FormWrapper>
	)
}

interface RenderChildrenFieldProps{
	childrenArr: Array<ChildrenType>
	childCount: number
	submitted: boolean
	onChangeChildName: (idx: number) => (e:any)=> void
	childInputClasses: (hasError: boolean) => string
}

const RenderChildrenField:React.FC<RenderChildrenFieldProps> = ({
	childrenArr,
	childCount,
	submitted,
	onChangeChildName,
	childInputClasses
})=>{
	return (
		<>
			{
				childCount > 0 && (
					childrenArr.slice(0,childCount).map((child,i:number)=>{
						const label = i > 0 ? ' and ' : ' named '
						const key = child.id || i
						return(
							<Col span={24} key={key}>
								<TinyP
									className={`
											text-center
											color-deep-ocean
											font-supria-sans
											font-16
											weight-300
											font-24
										`}
									marginBottom={4}
								>
									{label}
								</TinyP>
								<AdjacentFormField
								>
									<Form.Item
										rules={[{ required: true, message: 'This field is required' }]}
										initialValue={childrenArr[i].firstName}
									>
										<Input
											onChange={onChangeChildName(i)}
											className={childInputClasses(
												submitted &&
											!childrenArr[i].firstName
											)}
											value={childrenArr[i].firstName}
											placeholder="Litte One's First Name"
										/>
										{
											submitted && !childrenArr[i].firstName && (
												<p className="HouseHoldInfoForm__input__label__error">
													This field is required
												</p>
											)
										}
									</Form.Item>
								</AdjacentFormField>
							</Col>
						)
					})
				)
			}
		</>
	)
}


export default HouseHoldInfoForm
