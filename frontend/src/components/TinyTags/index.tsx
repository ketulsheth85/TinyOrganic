import React from 'react'
import {Tag, Tooltip} from 'antd'
import {
	CheckCircleOutlined,
	SyncOutlined,
	CloseCircleOutlined,
	PieChartOutlined,
} from '@ant-design/icons'
import cx from 'classnames'

import { FulfillmentStatus } from 'api/OrderAPI/types'

export interface TinyTagProps{
	children: React.ReactNode
	type: FulfillmentStatus
	tooltipText?: string
	className?: string
}
const TinyTag:React.FC<TinyTagProps> = ({type, tooltipText, children, className})=>{
	const classes = cx('', {
		[`${className}`]: !!className
	})
	const infoText = tooltipText || type

	switch(type){
	case FulfillmentStatus.pending:
		return (
			<Tooltip title={infoText} color="blue">
				<Tag className={classes}  icon={<SyncOutlined spin />} color="processing">
					{children}
				</Tag>
			</Tooltip>	
		)
	case FulfillmentStatus.cancelled:
		return (
			<Tooltip title={infoText} color="red">
				<Tag className={classes}  icon={<CloseCircleOutlined />} color="error">
					{children}
				</Tag>
			</Tooltip>
		)
	case FulfillmentStatus.fulfilled:
		return (
			<Tooltip title={infoText} color="green">
				<Tag className={classes}  icon={<CheckCircleOutlined />} color="success">
					{children}
				</Tag>
			</Tooltip>
		)
	case FulfillmentStatus.partial:
		return (
			<Tooltip title={infoText} color="yellow">
				<Tag className={classes}  icon={<PieChartOutlined />} color="warning">
					{children}
				</Tag>
			</Tooltip>
		)
	default:
		return (
			<Tooltip title={infoText} color="blue">
				<Tag className={classes}  icon={<SyncOutlined spin />} color="processing">
					{children}
				</Tag>
			</Tooltip>	
		)
	}
}

export default TinyTag
