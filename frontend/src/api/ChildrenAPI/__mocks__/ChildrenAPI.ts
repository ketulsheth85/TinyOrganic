import { omit } from 'lodash'
import { ChildrenCreationPayload, ChildrenType } from '../types'

class ChildrenAPI {

	protected _data(data: any) {
		return data
	}

	async create(
		child:ChildrenCreationPayload,
		parentID: string
	): Promise<ChildrenType>{
		return new Promise((resolve,reject)=>{
			if(!parentID){
				reject(new Error ('parent id is a required field'))
			}
			const _child = this._data(child) as ChildrenType
			resolve(_child)
		})
	}

	async update(
		child:Partial<ChildrenType>
	): Promise<ChildrenType>{
		return new Promise((resolve,reject)=>{

			if(Object.keys(child).length === 0){
				reject(new Error('at least one child field is required'))
			}

			if(!child.id){
				reject(new Error(`id of "${child.id}" is not a valid id`))
			}

			const _child = this._data(omit(child,['parent','id'])) as ChildrenType
			resolve(_child)
		})
	}

	async delete(
		childID: string
	): Promise<void>{
		return new Promise((resolve,reject)=>{

			if(!childID){
				reject(new Error(`id of "${childID}" is not a valid id`))
			}
			resolve()
		})
	}
}


export default new ChildrenAPI()
