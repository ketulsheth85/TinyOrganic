import DiscountAPI from 'api/DiscountAPI'


interface YotpoMethodsMembers{
fields: Omit<YotpoMethods, 'is_yotpo_url' | 'getDiscountFromReferralLink'>,
actions: Pick<YotpoMethods, 'is_yotpo_url'| 'getDiscountFromReferralLink'>
}

const useYotpoMethods = ():YotpoMethodsMembers =>{
	const yotpoMethods = new YotpoMethods()

	// keep the external api somewhat consistent with other hooks
	return {
		fields: yotpoMethods,
		actions: yotpoMethods
	}
}


class YotpoMethods{
	private REFERRAL_PROGRAM_UTM_CAMPAIGN = 'referral_program'
	private REFERRAL_UTM_SOURCE = 'loyalty'

	get params(){
	// This doesn't work in internet explorer
		return (new URL(document.location as any)).searchParams
	}

	get couponCode(){
		return this.params.get('sref_id') || ''
	}

	get utm_campaign(){
		return this.params.get('utm_campaign') || ''
	}

	get utm_source(){
		return this.params.get('utm_source') || ''
	}

	get is_yotpo_url(){
		return this.couponCode && 
	this.utm_campaign == this.REFERRAL_PROGRAM_UTM_CAMPAIGN &&
	this.utm_source == this.REFERRAL_UTM_SOURCE
	}

	async getDiscountFromReferralLink(){
		if(this.is_yotpo_url){
			return DiscountAPI.getDiscount({
				codename: this.couponCode
			}).catch(()=>{
				return
			})
		}
	}
}


export default useYotpoMethods
