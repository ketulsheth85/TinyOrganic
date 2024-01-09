import React from 'react'
import { isEmpty } from 'lodash'
import moment, {Moment} from 'moment'

import { ChildrenType } from 'api/ChildrenAPI/types'
import { RenderChildOrderInfoViewControllerMembers } from '../RenderChildOrderInfo/vc'
import RenderChildOrderButtons from '../RenderChildOrderButtons'
import RenderChildWithSubscriptionViewController from './vc'
import { Button, Col, DatePicker, Form, Row } from 'antd'
import { EditableInfoFormCard } from 'src/shells/EditableInfoForm'
import { TinyP } from 'components/Typography'
import TinyModal from 'src/shells/TinyModal'
import RenderLineItems from '../RenderLineItems'
import { ButtonContainer } from 'src/shells/FormWrapper'
import RenderMealPlan from '../RenderMealPlans'
import TinyTag from 'components/TinyTags'
import RenderEditChildInfoModal from '../RenderEditChildInfoModal'
import RenderAllergyWarningModal from '../RenderAllergyWarningModal'



interface RenderChildWithSubscription{
	childrenWithSubcriptions: Array<ChildrenType>
	renderChildOrderInfoViewController: RenderChildOrderInfoViewControllerMembers
}

const RenderChildWithSubscription:React.FC<RenderChildWithSubscription> = ({
	renderChildOrderInfoViewController,
	childrenWithSubcriptions
})=>{

	return (
		<div>
			{
				childrenWithSubcriptions.map((child)=>{
					const {
						fields: {
							firstName,
							childOrder,
							chargeDate,
							subscription,
							shouldHideHeaderInfo,
							receipesWithAllergies,
							childCart,
							isSubscriptionInactive,
							currentSubscriptionTitle,
							shouldShowhowMealPlan,
							childSubscription,
							lastDateToMakeChanges,
							shouldShowReactiveSubscriptionModal,
							childOrderItems,
							subscriptionLineItems,
							shouldShowDatePicker,
							shouldShowChildInfo,
							shouldShowAllergyWarningModal,
						},
						actions
					} = RenderChildWithSubscriptionViewController(
						child,
						renderChildOrderInfoViewController,
					)

					const shippingDateCopy = actions.getShippingDateCopy(childOrder.chargedAt)
					const currentSubscriptionChildComponent = (()=>(
						<>
							{
								!shouldHideHeaderInfo && (
									<RenderChildOrderButtons
										childName={firstName}
										isSubscriptionInactive={isSubscriptionInactive} 
										onEditOrderDate={actions.showDatePicker}
										onEditMeals={actions.showMealPlan}
										onEditChildInfo={actions.showChildInfoModal}
									/>
								)
							}
						</>
					))

					const disabledDate = (date: Moment)=>{
						return date.isBefore(moment()) || date.isAfter(moment().add(60, 'days'))
					}

					return (
						<Col key={`RenderChildWithSubscription-${child.id}`} span={36}>
							<Row>
								{!shouldHideHeaderInfo && (
									<Col span={24}>
										<EditableInfoFormCard
											title={`${firstName}'s Current Order`}
											open={true}
											setOpen={()=> {/** */}}
											isEditable={false}
										>	
											<Row gutter={64}>
												{isEmpty(childOrder) && (
													<Col className="margin-top-20" span={24}>
														<TinyP>
															We could not retrieve an order for this child, if you believe this in an error,
															please reload the page. if this error persists, contact customer service.
														</TinyP>
													</Col>
												)}
												{!isEmpty(childOrder) && (
													<>
														<Col span={24} md={12}>
															<TinyP className='margin-top-20 font-16' lineHeight={7}>
																<strong>Shipping Information:</strong> <br/>
																{childOrder.chargedAt && (
																	<>
																		<strong>Charge date #: </strong> {moment(childOrder.chargedAt).format('MM/DD/YYYY')}
																		<br/>
																	</>
																)}
																{childOrder.trackingNumber && (
																	<>
																		<strong>Tracking #: </strong> {childOrder.trackingNumber}
																		<br/>
																	</>
																)}
																{childOrder.externalOrderId && (
																	<>
																		<strong>Order #:</strong> {childOrder.orderNumber}
																		<br/>
																	</>
																)}
															</TinyP>
															<TinyP className='margin-x-20 font-16' lineHeight={7}>
																<strong>Estimated Ship Date:</strong> <br/>
																{shippingDateCopy}
															</TinyP>
														</Col>
														<Col span={24} md={12}>
															<TinyP className='margin-x-20 font-16' lineHeight={7}>
																<strong>Fulfillment Status:</strong> <br/>
																{
																	<TinyTag tooltipText={actions.getFulfillmentStatusToolTipText(childOrder.fulfillmentStatus)} type={childOrder.fulfillmentStatus}>
																		{childOrder.fulfillmentStatus}
																	</TinyTag>
																}
															</TinyP>
														</Col>
														<Col span={24} md={24}>
															<TinyP className='font-16 color-red' lineHeight={7}>
																<strong>Update: we are experiencing temporary shipping delays and apologize for the extended lead time</strong>
															</TinyP>
														</Col>
													</>
												)}
											</Row>

											<RenderLineItems lineItems={childOrderItems} />
										</EditableInfoFormCard>
									</Col>
								)}
								<Col span={24}>
									<EditableInfoFormCard
										title={currentSubscriptionTitle}
										open={true}
										setOpen={()=> {/** */}}
										ChildComponent={currentSubscriptionChildComponent}
									>
										{shouldShowhowMealPlan && (
											<RenderMealPlan
												title={`Updating ${firstName}'s Meal Plan`}
												updateBundleInfo={actions.updateBundleInfo}
												apiStatus={subscription.APIStatus}
												childSubscription={childSubscription}
												childCart={childCart}
												currentChild={child}
												customer={subscription.id}
												onBack={actions.hideMealPlan}
												onSubmit={actions.onSubmitMealPlan(actions.hideMealPlan)}
												allergies={child.allergies}
												analyticsInfo={{
													first_name: subscription.firstName,
													last_name: subscription.lastName,
													email: subscription.email
												}}
											/>
										)}
										{shouldShowChildInfo && (
											<RenderEditChildInfoModal
												isModalVisible={shouldShowChildInfo}
												onCloseModal={actions.hideChildInfoModal}
												currentChild={child}
												onSubmit={(allergies: Array<string>)=>{
													actions.hideChildInfoModal()
													actions.shouldShowRecipeWarningModal(allergies)
												}}
											/>
										)}
										{shouldShowAllergyWarningModal && (
											<RenderAllergyWarningModal 
												child={child}
												isModalVisible={shouldShowAllergyWarningModal}
												onClose={actions.hideAllergyWarningModal}
												recipesWithAllergies={receipesWithAllergies}
											/>
										)}
										{!shouldShowhowMealPlan &&(
											<>
												{!isSubscriptionInactive && (
													<>
														<TinyP lineHeight={7} className='margin-x-20 font-16'
														>
														An order for <strong>{childSubscription.numberOfServings}</strong> meals will process every 
															<strong> {childSubscription.frequency}</strong> weeks. 
														You can make changes to your next order until <strong>{lastDateToMakeChanges} </strong> at 
															<strong> 11:59PM EST</strong>.
														</TinyP>
														<TinyP
															className='font-16'
														>
														Next Charge Date: <strong>{chargeDate.format('MM/DD/YYYY')}</strong>
															<strong>{' '}Note:</strong> once charged, orders typically ship out within 2-4 business days.
														</TinyP>
													</>
												)}
												{isSubscriptionInactive && (
													<>
														
														<TinyP 
															lineHeight={7}
															className="font-16 margin-top-20 margin-bottom-12"
														>
															{`${firstName}'s`} subscription is <strong>inactive</strong>. You can still make changes to their subscription,
															but no additional orders will process until you <strong>reactivate</strong> their subscription.
														</TinyP>
														<div className="margin-bottom-36">
															<Button onClick={()=> actions.setShouldShowReactivateSubcriptionModal(true)} type="primary" size="large" shape="round">
																Reactivate {`${firstName}'s`} Subscription 🎉
															</Button>
														</div>
														<TinyModal
															isModalVisible={shouldShowReactiveSubscriptionModal}
															title={`Reactivate ${firstName}'s Subscription`}
														>
															<TinyP className="really-dude font-16 weight-400" lineHeight={5}>
															By reactivating this subscription, an order will begin <strong>processing immediately</strong> and the payment
															method on file will be charged. Your order will process with your current meal selections 
															(if you’d like to adjust meals, please do so before reactivating). 
															Please refer to your order confirmation email for full order details.
															</TinyP>
															<TinyP className="really-dude font-16 weight-400" lineHeight={5}>
																<strong><em>Note: Please allow up to 60 minutes for your order confirmation email to arrive and your 
																account dashboard to reflect your new order information!</em></strong> 
															</TinyP>
															<div className="padding-top-20">
																<Button 
																	className="margin-right-8"
																	shape="round" 
																	onClick={actions.reactiveChildSubscription} 
																	type="primary">
																	Reactivate Subscription + Place Order 🎉
																</Button>
																<Button
																	className="padding-0" 
																	shape="round"
																	onClick={()=> actions.setShouldShowReactivateSubcriptionModal(false)} 
																	type="default" 
																	size="small">
																	I&apos;m not quite ready yet
																</Button>
															</div>
														</TinyModal>
													</>
												)}
												<RenderLineItems 
													lineItems={subscriptionLineItems}
													allergies={child.allergies}
													firstName={child.firstName}
												/>
											</>
										)}
									</EditableInfoFormCard>
								</Col>
							</Row>
							<TinyModal
								title={'Change Charge Date'}
								isModalVisible={shouldShowDatePicker}
								closable={false}
							>
								<TinyP
									className={`
											font-16
											color-deep-ocean
											weight-500
											text-center
											margin-bottom-20
										`}
									lineHeight={5}
								>
										Note: once charged, orders typically ship out within 2-4 business days 
								</TinyP>
								<Form
									onFinish={actions.updateChargeDate(
										childSubscription.id,
										actions.setShouldShowDatePicker
									)}
									initialValues={{
										chargeDate
									}}
								>
									<Form.Item
										name="chargeDate"
										rules={[{required: true, message: 'Please Enter a Charge date'}]}
									>
										<DatePicker 
											placeholder="MM/DD/YYYY"
											format="MM/DD/YYYY"
											disabledDate={disabledDate}
											size="large"
										/>
									</Form.Item>
									<ButtonContainer 
										unstickyOnMobile
										className={`
												margin-x-auto-important
												max-width-326
											`}
									>

										<Button 
											type="primary"
											size="large"
											htmlType="submit"
										>
												Submit
										</Button>
										<Button 
											type="default"
											size="large"
											onClick={()=> (
												actions.setShouldShowDatePicker(false)	
											)}
										>
												Cancel
										</Button>
									</ButtonContainer>
								</Form>
							</TinyModal>
						</Col >
					)
				})
			}
		</div>
	)
}

export default RenderChildWithSubscription
