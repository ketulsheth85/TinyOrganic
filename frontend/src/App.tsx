import React from 'react'
import { Provider } from 'react-redux'
import { BrowserRouter as Router, Route } from 'react-router-dom'
import { ToastContainer } from 'react-toastify'

import store from 'store/store'
import ErrorBoundary from './shells/ErrorBoundary'
import OnboardingPage from 'pages/OnboardingPage'
import PostPurchasePage from 'pages/PostPurchasePage'
import DashboardPage from 'pages/DashboardPage'

import 'antd/dist/antd.css'
import 'react-toastify/dist/ReactToastify.css'
import './styles/main.scss'

const App:React.FC = () => {
	return (
		<div>
			<ErrorBoundary>
				<>
					<Provider store={store}>
						<Router>
							<Route
								exact={false}
								path="/onboarding/"
								render={()=>(<OnboardingPage />)}
							/>
							<Route
								exact={true}
								path="/post-purchase" 
								render={()=>(<PostPurchasePage/>)}
							/>
							<Route
								exact={false}
								path="/dashboard/"
								render={()=>(<DashboardPage/>)}
							/>
						</Router>
					</Provider>
					<ToastContainer/>
				</>
			</ErrorBoundary>
		</div>
	)
}

export default App
