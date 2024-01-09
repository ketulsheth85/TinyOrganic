import React, { useContext, useState } from 'react'
import { Button } from 'antd'
import { MenuOutlined, CloseOutlined } from '@ant-design/icons'
import cx from 'classnames'
import {Link, RouteProps, useHistory, RouteComponentProps} from 'react-router-dom'

import './styles.scss'

export interface NavigationProps{
	children?: React.ReactNode
}

const NavigationContext = React.createContext({
	closeMenu: () => {/** */}
})

const Navigation:React.FC<NavigationProps> = ({
	children
})=>{
	const [isOpen, setIsOpen] = useState(false)
	const toggleIsOpen = ()=> setIsOpen((open)=> !open)
	const navigationItemClasses = cx('Navigation__links', {
		'Navigation__links--open': isOpen
	})
	const closeMenu = ()=> setIsOpen(false)
	return (
		<div className="Navigation">
			<div className="Navigation__inner">
				<div className="Navigation__logo">
					<a href="https://www.tinyorganics.com">
						<img
							src="https://cdn.shopify.com/s/files/1/0018/4650/9667/files/TINY-fullcolor-xwhitespace.png?v=1585325388" 
							alt="Tiny Organics logo - Go to www.tinyorganics.com"
						/>
					</a>
				</div>
				{!!children && (
					<>
						<Button 
							type="link" 
							className="Navigation__button"
							onClick={toggleIsOpen}
						>
							{isOpen ?  <CloseOutlined /> : <MenuOutlined />}
						</Button>
						<div className="Navigation__items">
							<ul className={navigationItemClasses}>
								<NavigationContext.Provider value={{closeMenu}}>
									{children}
								</NavigationContext.Provider>
							</ul>
						</div>
					</>
				)}
			</div>
		</div>
	)
}

export interface NavigationItem{
	href: string
	children: React.ReactChild
	active?: boolean
}
export const NavigationLink:React.FC<NavigationItem> = ({
	href,
	children,
	active,
})=>{
	const history = useHistory<RouteProps>()
	const {closeMenu} = useContext(NavigationContext)
	const is_active_function = (history: RouteComponentProps['history'])=> history.location.pathname === href
	const _active = active !== undefined ? active : is_active_function(history)
	const classes = cx('Navigation__link', {
		'Navigation__link--active': _active
	})

	return (
		<li onClick={closeMenu} className={classes}>
			<Link to={href}>
				{children}
			</Link>
		</li>
	)
}

export default Navigation
