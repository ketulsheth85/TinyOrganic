import React, { ReactNode } from 'react'
import cx from 'classnames'
import {Properties} from 'csstype'
  
import {classPrefixer, fourDpUnit} from 'src/utils/utils'

interface TinyHeaderProps {
  className?: string
  tag?: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6'
  children: ReactNode
  style?: Properties
}
const CLASS_NAME = 'TinyHeader'
const px = classPrefixer(CLASS_NAME)

const TinyHeader: React.FC<TinyHeaderProps> = ({ className,tag,children,...rest}) => {
	const classes = cx(px(CLASS_NAME), {
		[`${className}`]: className,
	})

	switch (tag) {
	case 'h1':
		return <h1 {...rest} className={classes}>{children}</h1>
	case 'h2':
		return <h2 {...rest} className={classes}>{children}</h2>
	case 'h3':
		return <h3 {...rest} className={classes}>{children}</h3>
	case 'h4':
		return <h4 {...rest} className={classes}>{children}</h4>
	case 'h5':
		return <h5 {...rest} className={classes}>{children}</h5>
	case 'h6':
		return <h6 {...rest} className={classes}>{children}</h6>
	default:
		return <h1 {...rest} className={classes}>{children}</h1>
	}
}

export default TinyHeader

interface HxProps {
  className?: string
  tag?: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6'
  lineHeight?: number
  marginBottom?: number
  children: ReactNode
}

export const Hx: React.FC<HxProps> = ({className,children,tag,lineHeight,marginBottom, ...rest}) => {
	const classes = cx(`HX-${tag || 'h1'} typography`, {
		[`${className}`]: className,
	})
	const styles = {
		...(lineHeight &&{lineHeight: fourDpUnit(lineHeight)}),
		...(marginBottom &&{marginBottom: fourDpUnit(marginBottom)}),
	}
	return (
		<TinyHeader style={styles} className={classes} tag={tag} {...rest}>
			{children}
		</TinyHeader>
	)
}

export const TinyP:React.FC<Omit<HxProps, 'tag'>> = ({className, lineHeight, marginBottom, children, ...rest})=>{
	const classes = cx('TinyP typography', {
		[`${className}`]: className,
	})
	const styles = {
		...(lineHeight &&{lineHeight: fourDpUnit(lineHeight)}),
		...(!isNaN(marginBottom as number) &&{marginBottom: fourDpUnit(marginBottom as number)}),
	}

	return (
		<p className={classes} style={styles} {...rest}>{children}</p>
	)
}
