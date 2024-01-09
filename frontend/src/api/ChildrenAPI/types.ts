import { Ingredient } from 'api/IngredientAPI/types'

export type ChildrenAllergySeverity = 'none' | 'allergic'

export type ChildrenType = {
    id: string
    firstName: string
    birthDate?: string
    parent: string
    sex?: string
    allergies?: Array<Ingredient>
    allergySeverity?: ChildrenAllergySeverity
}

export type ChildrenCreationPayload = Partial<ChildrenType>

export type ChildrenAllergyUploadPaylaod = {
    allergies?: Array<string>
}
export type ChildrenUpdatePayload = Omit<Partial<ChildrenType>, 'allergies' > & ChildrenAllergyUploadPaylaod

export type ChildrenID = string
