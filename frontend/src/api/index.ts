/* eslint-disable no-mixed-spaces-and-tabs */
import axios, { 
	AxiosRequestConfig,
	AxiosResponse,
	AxiosInstance
} from 'axios'

export type ClientAPIConfig = AxiosRequestConfig
export type QueryArgsObj = Record<string, string | number>

const getCsrfCookie = ()=>{
	return document.cookie
		.split('; ')
		.find(
			(str)=> str.includes('csrftoken')
		) || 'csrftoken=csrftoken'
}

class API {
  private config: ClientAPIConfig

  private defaultConfig = {
  	returnRejectedPromiseOnError: true,
  	withCredentials: true,
  	timeout: 30000,
  	xsrfCookieName: 'csrftoken',
  	xsrfHeaderName: 'X-XSRF-TOKEN',
  	headers: {
  		'Content-Type': 'application/json',
  		Accept: 'application/json',
  	}
  }

  private api: AxiosInstance;

  constructor(config: ClientAPIConfig) {
  	this.config = {
  		...this.defaultConfig,
  		...config
  	}
  	this.api = axios.create(this.config)
  }

  get client():AxiosInstance {
  	const csrfCookie = getCsrfCookie()
  	this.api.defaults.headers.common['X-CSRFToken'] = csrfCookie.split('=')[1]
  	return this.api
  }

  _queryArgs(queryArgs?: QueryArgsObj):string{
  	let args = ''
  	const keys = Object.keys(queryArgs || {})
  	if(queryArgs && keys.length){
  		args = '?'
  		keys.forEach((key,i)=>{
  			if(i > 0) args += '&'
  			args += `${key}=${queryArgs[key]}`
  		})
  	}
  	return args
  }

  protected createDTO(data: any){
	  return data
  }

  protected _data(resp: AxiosResponse) {
  	return resp.data
  }

}

export default API
