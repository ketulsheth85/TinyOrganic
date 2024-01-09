import React from 'react'
import ReactDOM from 'react-dom'
import * as Sentry from '@sentry/react'
import { Integrations } from '@sentry/tracing'

import App from './App.tsx'

Sentry.init({
	// eslint-disable-next-line no-undef
	dsn: process.env.SENTRY_FRONTEND_DSN,
	integrations: [new Integrations.BrowserTracing()],
	tracesSampleRate: 0.1,
})

ReactDOM.render(<App />, document.getElementById('root'))
