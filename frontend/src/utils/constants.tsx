import { invert } from 'lodash'
import { ToastOptions } from 'react-toastify'

/**
 * Matches the following format CCC@CCC.CCC
 * Where C is any character under the sun that isn't a space
 */
export const EMAIL_REGEX = /^[^\s]{3,}@[^\s]{3,}\.[A-Z]{2,}$/gi

// matches 5 digits of this format #####
export const ZIP_CODE_REGEX = /^\d{5}$/

/**
 * 
 * Ripped this one from https://stackoverflow.com/questions/16699007/regular-expression-to-match-standard-10-digit-phone-number
 * 
 * should match the following formats with or whiteout space delimiters
 * 
 * 123-456-7890
 * (123) 456-7890
 * 123 456 7890
 * 123.456.7890
 * +91 (123) 456-7890
 *
 **/
export const PHONE_NUMBER_REGEX = /^(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$/

// no whitespace anywhere in string
export const NO_SPACE_REGEX = /^\S*$/

/**
 * Matches any reference to a PO BOX shipping address
 */
export const NO_PO_BOX_REGEX = /^(?!.*(?:(.*((p|post)[-.\s]*(o|off|office)[-.\s]*(box|bin)[-.\s]*)|.*((p |post)[-.\s]*(box|bin)[-.\s]*)))).*$/gi

export const STATE_OPTIONS = Object.freeze([
	{ name: 'Alabama', value: 'Alabama' },
	{ name: 'Arizona', value: 'Arizona' },
	{ name: 'Arkansas', value: 'Arkansas' },
	{ name: 'California', value: 'California' },
	{ name: 'Colorado', value: 'Colorado' },
	{ name: 'Connecticut', value: 'Connecticut' },
	{ name: 'Delaware', value: 'Delaware' },
	{ name: 'District Of Columbia', value: 'District Of Columbia' },
	{ name: 'Florida', value: 'Florida' },
	{ name: 'Georgia', value: 'Georgia' },
	{ name: 'Idaho', value: 'Idaho' },
	{ name: 'Illinois', value: 'Illinois' },
	{ name: 'Indiana', value: 'Indiana' },
	{ name: 'Iowa', value: 'Iowa' },
	{ name: 'Kansas', value: 'Kansas' },
	{ name: 'Kentucky', value: 'Kentucky' },
	{ name: 'Louisiana', value: 'Louisiana' },
	{ name: 'Maine', value: 'Maine' },
	{ name: 'Maryland', value: 'Maryland' },
	{ name: 'Massachusetts', value: 'Massachusetts' },
	{ name: 'Michigan', value: 'Michigan' },
	{ name: 'Minnesota', value: 'Minnesota' },
	{ name: 'Mississippi', value: 'Mississippi' },
	{ name: 'Missouri', value: 'Missouri' },
	{ name: 'Montana', value: 'Montana' },
	{ name: 'Nebraska', value: 'Nebraska' },
	{ name: 'Nevada', value: 'Nevada' },
	{ name: 'New Hampshire', value: 'New Hampshire' },
	{ name: 'New Jersey', value: 'New Jersey' },
	{ name: 'New Mexico', value: 'New Mexico' },
	{ name: 'New York', value: 'New York' },
	{ name: 'North Carolina', value: 'North Carolina' },
	{ name: 'North Dakota', value: 'North Dakota' },
	{ name: 'Ohio', value: 'Ohio' },
	{ name: 'Oklahoma', value: 'Oklahoma' },
	{ name: 'Oregon', value: 'Oregon' },
	{ name: 'Pennsylvania', value: 'Pennsylvania' },
	{ name: 'Rhode Island', value: 'Rhode Island' },
	{ name: 'South Carolina', value: 'South Carolina' },
	{ name: 'South Dakota', value: 'South Dakota' },
	{ name: 'Tennessee', value: 'Tennessee' },
	{ name: 'Texas', value: 'Texas' },
	{ name: 'Utah', value: 'Utah' },
	{ name: 'Vermont', value: 'Vermont' },
	{ name: 'Virginia', value: 'Virginia' },
	{ name: 'Washington', value: 'Washington' },
	{ name: 'West Virginia', value: 'West Virginia' },
	{ name: 'Wisconsin', value: 'Wisconsin' },
	{ name: 'Wyoming', value: 'Wyoming' }, 
])

export const STATES_HASH: Record<string,string> = Object.freeze({
	Alabama: 'AL',
	Arizona: 'AZ',
	Arkansas: 'AR',
	California: 'CA',
	Colorado: 'CO',
	Connecticut: 'CT',
	Delaware: 'DE',
	'District Of Columbia': 'DC',
	Florida: 'FL',
	Georgia: 'GA',
	Idaho: 'ID',
	Illinois: 'IL',
	Indiana: 'IN',
	Iowa: 'IA',
	Kansas: 'KS',
	Kentucky: 'KY',
	Louisiana: 'LA',
	Maine: 'ME',
	Maryland: 'MD',
	Massachusetts: 'MA',
	Michigan: 'MI',
	Minnesota: 'MN',
	Mississippi: 'MS',
	Missouri: 'MO',
	Montana: 'MT',
	Nebraska: 'NE',
	Nevada: 'NV',
	'New Hampshire': 'NH',
	'New Jersey': 'NJ',
	'New Mexico': 'NM',
	'New York': 'NY',
	'North Carolina': 'NC',
	'North Dakota': 'ND',
	Ohio: 'OH',
	Oklahoma: 'OK',
	Oregon: 'OR',
	Pennsylvania: 'PA',
	'Rhode Island': 'RI',
	'South Carolina': 'SC',
	'South Dakota': 'SD',
	Tennessee: 'TN',
	Texas: 'TX',
	Utah: 'UT',
	Vermont: 'VT',
	Virginia: 'VA',
	Washington: 'WA',
	'West Virginia': 'WV',
	Wisconsin: 'WI',
	Wyoming: 'WY',
})

export const STATE_REVERSE_HASH = Object.freeze(invert(STATES_HASH))


export const DEFAULT_TOAST_OPTIONS:ToastOptions = Object.freeze({
	position: 'bottom-right',
	autoClose: 5000,
	hideProgressBar: false,
	closeOnClick: true,
	pauseOnHover: true,
	draggable: false,
	progress: undefined,
})

export const TOP_CENTER_PERSISTENT_TOAST_OPTIONS:ToastOptions = Object.freeze({
	position: 'top-center',
	autoClose: false,
	hideProgressBar: true,
	closeOnClick: true,
	pauseOnHover: true,
	draggable: false,
	progress: undefined,
})


export const TWELVE_PACK_MEAL_PRICE = 5.49
export const TWENTY_FOUR_PACK_MEAL_PRICE = 4.69

export const YOTPO_REFERRAL_LINK_BASE_URL = 'http://rwrd.io'

export const SHARE_A_SALE_ORDERS_TO_TRACK = 'SHARE_A_SALE_ORDER_TO_TRACK'
export const SHARE_A_SALE_COUPON_TO_ADD = 'SHARE_A_SALE_COUPON_TO_ADD'
export const SHARE_A_SALE_ORDER_SUMMARY = 'SHARE_A_SALE_ORDER_SUMMARY'
