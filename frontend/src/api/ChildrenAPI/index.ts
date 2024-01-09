import API from '..'
import {
	ChildrenType,
	ChildrenCreationPayload,
	ChildrenUpdatePayload
} from './types'
import { conditionalOmit } from 'src/utils/utils'

const BACKEND_URL = '/api'
export class ChildrenAPI extends API{

	protected sanitizeChild(child:Partial<ChildrenType>):Partial<ChildrenType>{
		const {
			sex,
			birthDate,
		} = child

		return conditionalOmit(child,{
			sex: !sex,
			birthDate: !birthDate,
			id: true
		})
	}

	protected createDTO(data:Partial<ChildrenType>): Partial<ChildrenType> {
		return this.sanitizeChild(data)
	}

	async create(
		child:ChildrenCreationPayload,
		parentID: string
	): Promise<ChildrenType>{

		/**
		 * gut check to make sure we don't create
		 * a child that already exists
		 **/ 
		if(child.id){
			throw Error('child already exists')
		}

		return this.client
			.post('/v1/customers-children/', this.createDTO({
				...child,
				parent: parentID
			}))
			.then((res) => this._data(res) as ChildrenType)
	}

	async update(
		child:ChildrenUpdatePayload
	): Promise<ChildrenType>{
		// eslint-disable-next-line @typescript-eslint/no-unused-vars
		const {id,parent, ..._child} = child
		return this.client
			.patch(`/v1/customers-children/${id}/`,_child)
			.then((resp)=>{
				return this._data(resp) as ChildrenType
			})
	}

	async delete(
		childID: string
	): Promise<void>{
		return this.client
			.delete(`/v1/customers-children/${childID}/`)
	}
}

// IAM API singleton
export default new ChildrenAPI({
	baseURL: BACKEND_URL 
})
