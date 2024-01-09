import React, { Fragment, useEffect, useState } from 'react'
import {
	Form,
	Row,
	Col,
	DatePicker,
	Select,
	Button
} from 'antd'
import { startsWith } from 'lodash'
import { isRejectedWithValue } from '@reduxjs/toolkit'
import {useDispatch, useSelector} from 'react-redux'
import moment,{ Moment } from 'moment'

import { getIngredients } from 'store/ingredientSlice'
import {SubscriptionSliceState, updateChild} from 'src/store/subscriptionSlice'
import FormWrapper, { ButtonContainer } from 'src/shells/FormWrapper'
import { MultipageFormComponentProps } from 'src/shells/MultiPageForm'
import { ChildrenAllergySeverity, ChildrenType, ChildrenUpdatePayload } from 'api/ChildrenAPI/types'
import { AppDispatch, RootState } from 'store/store'
import { TinyP } from 'components/Typography'
import { SplashPage } from 'components/OnboardingSplashPage'
import analyticsClient from 'src/libs/analytics'
import { Ingredient } from 'api/IngredientAPI/types'


export interface ChildrenInformationFormPayload{
	sex: string
	allergies?: Array<string>
	allergySeverity: ChildrenAllergySeverity
	birthDate: Moment
}
export interface ChildrenInformationFormProps{
	store?: SubscriptionSliceState // only used in onboarding
	currentChild: ChildrenType
	onSubmit: (children: ChildrenUpdatePayload) => void
	onBack?: (shouldLoop?: boolean) => void
	onBackCta?: string
	withHeader?: boolean // usually only used in onboarding
	loading?: boolean
}

/**
 	store prop is only use for onboarding analytics, don't use pass store
	into component when used outside analytics context.
 */
export const ChildrenInformationForm:React.FC<ChildrenInformationFormProps> = ({
	store,
	onSubmit,
	currentChild,
	onBack,
	withHeader,
	onBackCta = 'Back',
	loading
})=>{

	const {
		ingredients,
		ingredientsMap
	} = useSelector((state:RootState)=> state.ingredient)
	const subscription = useSelector((state: RootState)=> state.subscription)

	const {
		firstName,
		birthDate,
		sex,
		allergies,
		allergySeverity,
		id
	} = currentChild
	/**
	 * maps children array of strings to array of Ingredient objects
	 * by checking the children allergies and the ingredients map for
	 * the string's corresponding object
	 */
	const ingredientNamesArrayToIngredientIdArray = (childAllergies: Array<string>)=>{
		const childIngredientMap = (allergies || [])
			.reduce((acc:Record<string, Ingredient>, curr)=>{
				acc[curr.name] = curr
				return acc
			}, {})

		return childAllergies
			.map((name)=>{
				if(childIngredientMap[name]){
					return childIngredientMap[name].id
				}
				return ingredientsMap[name].id
			})
			.filter(Boolean)
	}

	useEffect(() => {
		if (birthDate && sex) {
			if((window as any).analytics){
				(window as any).analytics.track('Updated Child Information', {
					email: subscription.email,
					first_name: subscription.firstName,
					last_name: subscription.lastName,
					child: {
						birth_date: birthDate,
						first_name: firstName,
						gender: sex,
					}
				})
			}
		}
	}, [birthDate, firstName])

	const _onSubmit = (payload:ChildrenInformationFormPayload) =>{
		let childAllergies:Array<string> = []

		if(payload.allergies){
			childAllergies = ingredientNamesArrayToIngredientIdArray(postFilteredlocalIngredients)
		}

		onSubmit({
			...payload,
			allergies: childAllergies,
			id,
			birthDate: payload.birthDate.format('YYYY-MM-DD')
		})
	}

	const disabledDate = (date: Moment)=>{
		return date.isAfter(moment.now())
	}

	const dispatch = useDispatch()

	const [postFilteredlocalIngredients, setPostFilteredlocalIngredients] = useState<Array<string>>([])
	const [preFilteredLocalIngredients, setPreFilteredLocalIngredients] = useState<Array<string>>([])
	const [invalidIngredientMessage, setInvalidIngredientMessage] = useState(' ')

	const [showAllergies, setShowAllergies] = useState(
		allergySeverity && allergySeverity !== 'none'
	)

	const _setLocalIngredients = (allergens:Array<string>) => {
		const ingredientsSet = new Set(ingredients)
		const _allergens = Array.from(new Set(allergens.map(allergen => allergen.toLowerCase()))) // lowercase, filter out duplicates with set, turn back to array
		const validIngredients = _allergens.filter((ingredient) => ingredientsSet.has(ingredient))
		
		setPreFilteredLocalIngredients(_allergens)
		setPostFilteredlocalIngredients(validIngredients)
	}

	const getInvalidIngredientMessage = (postFilteredlocalIngredients:Array<string>) => {
		const ingredientsSet = new Set(ingredients)
		const invalidIngredients = preFilteredLocalIngredients.filter((ingredient) => !ingredientsSet.has(ingredient))

		if(invalidIngredients.length) {
			return `The ingredients ${invalidIngredients.join(', ')} are not in any of our recipes and will not be added to your child's allergies.`
		}

		return ''
	}

	useEffect(() => {
		setInvalidIngredientMessage(getInvalidIngredientMessage(postFilteredlocalIngredients))
	}, [postFilteredlocalIngredients])

	const onSelectSeverity =(allergySeverity:string)=>{
		setShowAllergies(!!allergySeverity && allergySeverity !== 'none')
	}

	const _getIngredients = (e:any) =>{
		// no empty query search
		const query = e.target.value

		if(!query){
			return
		}

		// if value exists, don't request it
		const idx = ingredients.find((ingredient:string)=> {
			return startsWith(ingredient,query)
		})

		if(typeof idx === 'number'){
			return
		}

		dispatch(getIngredients(query))
	}

	// fetch some default values so allergies form is not empty
	useEffect(()=>{
		_getIngredients({target:{value: 'e'}})
		if(store){
			analyticsClient.pageView('Onboarding', 'Child Information', {
				first_name: store.firstName,
				last_name: store.lastName,
				email: store.email,
				child: firstName
			})
		}
	}, [])

	const initialValues = {
		sex: sex || 'male',
		birthDate: birthDate && moment(birthDate),
		allergySeverity: allergySeverity || 'none',
		allergies:allergies ? allergies.map(({name})=> name) : []
	}

	const formWrapperHeaderProps = {...(withHeader && {
		tagline:`We know ${firstName} will love Tiny Meals!`,
		title: `Tell us a little more about ${firstName}`,
		subtitle: 'This helps us make sure we\'re recommending the best possible meal plan for you and your little ones.'
	})}

	return (
		<FormWrapper
			{...formWrapperHeaderProps}
			className="OnboardingPageOverrides max-width-500 margin-x-auto"
		>
			<Col span={24}>
				<Form
					name="ChildrenInformationForm"
					autoComplete="off"
					validateTrigger="onBlur"
					onFinish={_onSubmit}
					initialValues={initialValues}
				>
					<Row>
						<Col span={24}>
							<Row gutter={32} align="middle">
								<Col span={12}>
									<Form.Item
										wrapperCol={{span: 24}}
										name="sex"
										rules={[{ required: true, message: 'This field is required' }]}
									>
										<Select
											placeholder="Select an Option"
										>
											<Select.Option value='male'>His</Select.Option>
											<Select.Option value='female'>Her</Select.Option>
											<Select.Option value='their'>Their</Select.Option>
											<Select.Option value='none'>Prefer not to say</Select.Option>  
										</Select>
									</Form.Item>
								</Col>
								<Col span={12}>
									<TinyP
										className={`
										color-deep-ocean
										font-supria-sans
										font-16
										weight-300
										font-24
								`}
									>
										Birthday is
									</TinyP>
								</Col>
							</Row>
						</Col>
						<Col span={24}>
							<Form.Item
								wrapperCol={{span: 24}}
								name="birthDate"
								rules={[{ required: true, message: 'This field is required' }]}
							>
								<DatePicker 
									placeholder="MM/DD/YYYY"
									format="MM/DD/YYYY"
									disabledDate={disabledDate}
									
								/>
							</Form.Item>
						</Col>
						<Col span={24}>
							<TinyP

								className={`
									max-width-326
									margin-x-auto
									text-center
									color-deep-ocean
									font-supria-sans
									font-16
									weight-300
									font-24
								`}
								marginBottom={4}
								lineHeight={9}
							>
								{`And when it comes to allergies, ${firstName} has`}
							</TinyP>
							<Form.Item
								wrapperCol={{span: 24}}
								name="allergySeverity"
							>
								<Select 
									style={{ width: '100%' }} 
									placeholder="no allergies"
									onChange={onSelectSeverity}	
								>
									<Select.Option value='none'>
											no allergies
									</Select.Option>
									<Select.Option value='allergic'>
											allergies
									</Select.Option>
								</Select>
							</Form.Item>
						</Col>
						<Col span={24} className={!showAllergies ? 'hidden' : ''}>
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
								To
							</TinyP>
							<Form.Item
								wrapperCol={{span: 24}}
								name="allergies"
							>
								<Select 
									mode="tags" 
									style={{ width: '100%' }} 
									placeholder="Allergies (start typing)"
									onKeyUp={_getIngredients}
									onChange={_setLocalIngredients}
								>
									{
										ingredients.map((value)=>{
											return (
												<Select.Option value={value} key={value}>
													{value}
												</Select.Option>
											)
										})
									}
								</Select>
							</Form.Item>
							{invalidIngredientMessage && (
								<TinyP
									marginBottom={6}
									lineHeight={7}
									className='color-evergreen-medium font-16'
								>
									{invalidIngredientMessage}
								</TinyP>
							)}
						</Col>
					</Row>
					<ButtonContainer unstickyOnMobile>
						<>
							<Button
								type="primary"
								size="large"
								htmlType="submit"
								loading={loading}
							>
								Continue
							</Button>
							{
								onBack && (
									<Button
										type="default"
										size="large"
										htmlType="button"
										disabled={loading}
										onClick={()=> {
											onBack()
										}}
									>
										{onBackCta}
									</Button>
								)
							}
						</>
					</ButtonContainer>
				</Form>
			</Col>
		</FormWrapper>
	)
}

const ChildrenInformationFormHOC:React.FC<MultipageFormComponentProps> = ({
	shouldSeeQuestion,
	onBack,
	onSubmit
}) =>{
	const [state,setState] = useState({
		cursor: 0,
		shouldRender: false
	})

	useEffect(()=>{
		const shouldRenderQuestion = shouldSeeQuestion(`
			It looks like you haven't gotten to "Children details" just yet,
			please fill out the form below to continue 😊
		`)
		if(shouldRenderQuestion){
			setState((state)=>{
				return {
					...state,
					shouldRender: true
				}
			})
		}
		
	}, [])

	const dispatch = useDispatch<AppDispatch>()
	const store = useSelector((state:RootState)=> state.subscription)

	const _onSubmit = (child:ChildrenUpdatePayload)=>{
		const shouldLoop =  state.cursor + 1 < store.children.length
		dispatch(updateChild(child))
			.then((action)=>{
				if(isRejectedWithValue(action)) return
				if(shouldLoop){
					setState(({cursor,...rest})=>{
						return {
							...rest,
							cursor: cursor+1,
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
			setState(({cursor, ...rest})=>{
				return {
					...rest,
					cursor: cursor-1
				}
			})
		}
		else if(onBack){
			onBack(shouldLoop)
		}
	}

	if(!state.shouldRender){
		return (
			<SplashPage />
		)
	}

	return (
		<>
			{store.children.map((child: ChildrenType, i:number)=>{
				return (
					<Fragment key={child.firstName}>
						{
							state.cursor === i && (
								<ChildrenInformationForm
									store={store}
									onSubmit={_onSubmit}
									currentChild={child}
									onBack={onBack && _onBack}
									withHeader
								/>
							)
						}
					</Fragment>
				)
			})}
		</>
	)
}
export default ChildrenInformationFormHOC
