import {toast, ToastOptions} from 'react-toastify'
import {defaultTo} from 'lodash'

import { DEFAULT_TOAST_OPTIONS } from 'src/utils/constants'


export const RenderSuccessToast = (message:string, options?:ToastOptions):void => {
	const _options = {...DEFAULT_TOAST_OPTIONS}
	Object.assign(_options,defaultTo(options, {}))
	toast.success(message, _options)
}


export const RenderErrorToast = (message:string, options?:ToastOptions):void => {
	const _options = {...DEFAULT_TOAST_OPTIONS}
	Object.assign(_options,defaultTo(options, {}))
	toast.error(message, _options)
}

export const RenderInfoToast = (message:string, options?:ToastOptions):void => {
	const _options = {...DEFAULT_TOAST_OPTIONS}
	Object.assign(_options,defaultTo(options, {}))
	toast.info(message, _options)
}

export const RenderDefaultToast = (message:string, options?:ToastOptions):void => {
	const _options = {...DEFAULT_TOAST_OPTIONS}
	Object.assign(_options,defaultTo(options, {}))
	toast(message, _options)
}
