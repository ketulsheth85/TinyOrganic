/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable @typescript-eslint/explicit-module-boundary-types */
import {
	cloneDeep,
	pick,
	startCase,
	toLower,
} from 'lodash'
import { RouteComponentProps } from 'react-router-dom'

export const camelCaseToTitleCase = (str:string):string =>{
	let s = ''

	for(let i = 0; i < str.length; i++){
		if(i === 0){
			s += str[i].toUpperCase()
		}
		else if(s[i-1] === '_'){
			s += str[i].toUpperCase()
		}
		else{
			s += str[i].toLowerCase()
		}
	}

	return s.replace(/_/g, ' ')
}

export const getCookieValue = (name:string ):string => (
	document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)')?.pop() || ''
)

export const removeCookie = (name:string ):void => {
	document.cookie = `${name}=;expires=${new Date(0).toUTCString()}`
}

export const deepClone = (obj:any) => cloneDeep(obj)

export const conditionalOmit = (obj:any, conditions:Record<any,boolean>) =>{
	const keys = Object.keys(conditions)
		.reduce((acc:Array<any>, curr)=>{
			if(conditions[curr]){
				acc.push(curr)
			}
			return acc
		}, [])
	const falsyKeys = new Set(keys)
	const truthyKeys = Object.keys(obj).filter((key)=>{
		return !falsyKeys.has(key)
	})
	return pick(obj, truthyKeys)
}


/**
 * creates function that prefixes a string with a className
 * using the following format className__string
 * @param className string to prefix class with
 */
export const classPrefixer = (className: string) => {
	return (str:string, separator='__') => `${className}${separator}${str}`
}
  
/**
   * creates a 4 dp unit given an integer
   * @param num - number to translate to 4dp grid unit
*/
export const fourDpUnit = (num: number) => `${num * 4}px`


export const titleCase = (str: string) => startCase(toLower(str))


export const getReferralCodeFromHistory = (history: RouteComponentProps)=>{
	//
}

export const segmentAnalitycs = (type: string, object: Record<any,any>) => {
	if ( (window as any).analytics && (window as any).analytics.track ) {
		(window as any).analytics.track(type, object)
	}
}
