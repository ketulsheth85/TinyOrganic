import {Product, ProductVariant} from 'api/ProductsAPI/types'

export type LineItemType = {
  id?: string,
  product: Product,
  productVariant?: ProductVariant,
  quantity: number,
}

export type CartType = {
  id: string,
  cartId: string
  customer: string,
  child: string,
  lineItems: Array<Partial<LineItemType>>,
}

export type CartUpdatePayload = {
  cartId: string,
  customerId: string,
  lineItems: Array<Partial<LineItemType>>
}
