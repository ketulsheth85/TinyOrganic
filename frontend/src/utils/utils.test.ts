import {
	getCookieValue,
	removeCookie,
	deepClone,
	conditionalOmit,
	camelCaseToTitleCase
} from './utils'

describe('utils ;) ', ()=>{

	test('camelCaseToTitleCase', ()=>{
		const strs = ['I_am_a_camel','reGular_string','nice_string']

		const str2 = strs.map(camelCaseToTitleCase)

		expect(str2).toEqual(['I Am A Camel','Regular String','Nice String'])
	})

	test('getCookieValue',()=>{
		document.cookie = 'key=value'
		document.cookie = 'no=thing'
		document.cookie = 'something=else'
	
		expect(getCookieValue('key')).toEqual('value')
		expect(getCookieValue('something')).toEqual('else')
		expect(getCookieValue('no')).toEqual('thing')
	})
	
	test('removeCookie', ()=>{
		document.cookie = 'cool=story-bro'
		expect(getCookieValue('cool')).toEqual('story-bro')
	
		removeCookie('cool')
		expect(getCookieValue('cool')).toEqual('')
	})
	
	
	test('deepClone', ()=>{
		const object ={
			weAre: 'not-the-same',
			tgi: 'friday',
			simple: 'plan'
		}
		const copy = deepClone(object)
	
		expect(object !== copy)
		expect(object).toMatchObject(copy)
	})
	
	test('conditionalOmit', ()=>{
		const object = {
			firstName: 'first',
			chocolateMilk: 'milk',
			super: 'visor',
			deleteMe: 'okay',
			takeMeOut: 'alright'
		}
	
		const newObject = conditionalOmit(object,{
			deleteMe: true,
			takeMeOut: ''.length === 0,
			super: false
		})
	
		expect(newObject).toMatchObject({
			firstName: 'first',
			chocolateMilk: 'milk',
			super: 'visor',
		})
	})
})
