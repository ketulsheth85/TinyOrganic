import React from 'react'

import './styles.scss'

export interface ErrorBoundaryProps {
	children: React.ReactChild
}

type ErrorBoundaryState = {
	hasError: boolean
}

class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
	constructor(props:ErrorBoundaryProps) {
		super(props)
		this.state = {
			hasError: false
		}
	}
	
	static getDerivedStateFromError():ErrorBoundaryState {
		return { hasError: true }
	}
  
	componentDidCatch():void {
		// Log error and errorInfo to Sentry
	}
  
	render():React.ReactNode {
		if (this.state.hasError) {
			return <RenderErrorPage />
		}

		return this.props.children 
	}
}

interface ErrorPageProps{
	message?: string
	children?: React.ReactNode
}
export const RenderErrorPage:React.FC<ErrorPageProps> = ({message, children})=>{
	return (
		<div className="RenderErrorPage">
			<div className="RenderErrorPage__inner">
				<div>
					{ message && (<h1>{message}</h1>) }
					{children && children}
					{!message && !children && (
						<h1>Something went wrong, please reload the page</h1>
					)}
				</div>
			</div>
		</div>
	)
}


export default ErrorBoundary
