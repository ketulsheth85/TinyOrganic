import { Ingredient } from 'src/api/IngredientAPI/types'

export type Product = {
	id: string
	title: string
	description?: string
	imageUrl: string
	price: number
	featuredIngredients?: string
	ingredients: Array<Ingredient>
	tags: Array<string>
	productType: string
	nutritionImageUrl?: string
	variants: Array<ProductVariant>
	showVariants: boolean
}

export type ProductVariant = {
	title?: string
	id: string
	skuId: string
	price: number
}

export type RecommendedProduct = {
	title: string
	containsAllergens: boolean
	product: Product,
	recipeId: string
}

export type RecommendedProducts = {
	tinyBeginnings: Array<RecommendedProduct>
	recommendations: Array<RecommendedProduct>
	remainingProducts: Array<RecommendedProduct>
}
