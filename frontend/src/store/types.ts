import { ChildrenCreationPayload } from 'api/ChildrenAPI/types'
import { GuardianType } from 'api/CustomerAPI/types'

export enum APIstatus {
	idle = 'idle',
	loading = 'loading',
	success = 'success',
	error = 'error'
}

export type ErrorPayload = {
	payload: string
}


export type HouseHoldInformationPayload = {
	children: Array<ChildrenCreationPayload>
	parentID: string,
	guardianType: GuardianType
}

export interface BaseReducerState {
	init: boolean
	error?: string
}

export interface BaseReducerStateAPI extends BaseReducerState{
	APIStatus: APIstatus
}
