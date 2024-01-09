import {
	isRejectedWithValue,
	Middleware,
} from '@reduxjs/toolkit'
import { toast } from 'react-toastify'
  
/**
 * Error logger middleware that logs an error
 * and adds a toast to the UI everytime we call
 * RejectWithValue in Redux Toolkit slices.
 * 
 * This middleware also throws an error so it
 * should used last. In addition, a catch clause
 * has to be added to all 
 */
const rtkQueryErrorLogger: Middleware =
	() => (next) => (action) => {
		if (isRejectedWithValue(action)) {
			const message = action.payload ||
			'something wen\'t wrong, please reload try again later'

			toast.error(message, {
				position: 'bottom-right',
				autoClose: 5000,
				hideProgressBar: false,
				closeOnClick: true,
				pauseOnHover: true,
				draggable: false,
				progress: undefined,
			})
		}

		return next(action)
	}

export default rtkQueryErrorLogger
