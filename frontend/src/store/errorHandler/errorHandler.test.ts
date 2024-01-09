import { cloneDeep } from 'lodash'
import { Dispatch, MiddlewareAPI } from 'redux'
import {toast} from 'react-toastify'

const toastSpy = jest.spyOn(toast, 'error')
jest.mock('@reduxjs/toolkit', ()=>{
	return {
		isRejectedWithValue: (action:any)=>{
			return action.rejectedWithValue === true
		}
	}
})

import errorHandler from './'


describe('Error handler middleware', ()=>{
	
	const mockNext = jest.fn((()=>{
		// nothing
	}))
	const next = mockNext as Dispatch<any>
	const action = {
		error: {
			message: 'Rejected'
		},
		meta:{
			aborted: false
		},
		arg: {
			email: 'danyisaboy@gmail.com',
			firstName: 'Dany',
			lastName: 'Boy'
		},
		condition: false,
		rejectedWithValue: true,
		requestId: 'tLL8XeLdnmEdki7scPIUU',
		requestStatus: 'rejected',
		payload: 'There was an error creating your account, please try again later',
		type: 'subscription/createConsumer/rejected'

	}
	const api = jest.fn as unknown as MiddlewareAPI

	test('Calls toast with error and moves on to next middleware', ()=>{
		errorHandler(api)(next)(action)

		expect(toastSpy).toHaveBeenCalledWith('There was an error creating your account, please try again later',
			{
				position: 'bottom-right',
				autoClose: 5000,
				hideProgressBar: false,
				closeOnClick: true,
				pauseOnHover: true,
				draggable: false,
				progress: undefined,
			}
		)
		expect(mockNext).toHaveBeenCalledWith(cloneDeep(action))
	})

	test('Calls toast with error with default message when none is provided', ()=>{
		const _action = cloneDeep(action)
		_action.payload = ''
		errorHandler(api)(next)(_action)

		expect(toastSpy).toHaveBeenCalledWith('something wen\'t wrong, please reload try again later',
			{
				position: 'bottom-right',
				autoClose: 5000,
				hideProgressBar: false,
				closeOnClick: true,
				pauseOnHover: true,
				draggable: false,
				progress: undefined,
			}
		)
		expect(mockNext).toHaveBeenCalledWith(cloneDeep(cloneDeep(_action)))
	})

	test('Calls middleware but does create toast for non error payload', ()=>{
		const _action = cloneDeep(action)
		_action.rejectedWithValue = false
		errorHandler(api)(next)(_action)
		expect(toastSpy).not.toHaveBeenCalled()
		expect(mockNext).toHaveBeenCalledWith(cloneDeep(_action))
	})
})
