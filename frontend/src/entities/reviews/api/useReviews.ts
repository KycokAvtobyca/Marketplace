import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { api } from "@/shared/api"
import { ROUTES } from "@/shared/config"

export interface Review {
  id: number
  product_variant: number
  rating: number
  description: string
  status: "PENDING" | "APPROVED" | "REJECTED"
  is_verified_purchase: boolean
  useful_count: number
  unuseful_count: number
  current_user_vote: "USEFUL" | "UNUSEFUL" | null
  author_name: string
  user_id: number | null
  date_time_create: string
  date_time_update: string
  images: Array<{ id: number; image: string }>
}

export interface ProductQuestion {
  id: number
  product: number
  product_name: string
  text: string
  answer: string
  author_name: string
  user_id: number | null
  answered_by_name: string
  answered_at: string | null
  is_public: boolean
  date_time_create: string
}

export const useProductReviews = (productId: number) => {
  return useQuery<Review[]>({
    queryKey: ["reviews", "product", productId],
    queryFn: async () => {
      const { data } = await api.get(`${ROUTES.REVIEWS.ROOT}?product=${productId}`)
      return data.results || data
    },
    enabled: !!productId,
    retry: 1,
  })
}

export const useCreateReview = (productId: number) => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (payload: {
      product_variant: number
      rating: number
      description: string
    }) => {
      const { data } = await api.post(ROUTES.REVIEWS.ROOT, payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reviews", "product", productId] })
      queryClient.invalidateQueries({ queryKey: ["product", productId] })
    },
  })
}

export const useUpdateReview = (productId: number) => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({
      id,
      rating,
      description,
    }: {
      id: number
      rating: number
      description: string
    }) => {
      const { data } = await api.patch(ROUTES.REVIEWS.RETRIEVE(id), {
        rating,
        description,
      })
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reviews", "product", productId] })
      queryClient.invalidateQueries({ queryKey: ["product", productId] })
    },
  })
}

export const useDeleteReview = (productId: number) => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete(ROUTES.REVIEWS.RETRIEVE(id))
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reviews", "product", productId] })
      queryClient.invalidateQueries({ queryKey: ["product", productId] })
    },
  })
}

export const useVoteReview = (productId: number) => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({
      id,
      value,
    }: {
      id: number
      value: "USEFUL" | "UNUSEFUL"
    }) => {
      const { data } = await api.post(ROUTES.REVIEWS.VOTE(id), { value })
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reviews", "product", productId] })
    },
  })
}

export const useProductQuestions = (productId: number) => {
  return useQuery<ProductQuestion[]>({
    queryKey: ["questions", "product", productId],
    queryFn: async () => {
      const { data } = await api.get(
        `${ROUTES.REVIEWS.QUESTIONS}?product=${productId}`,
      )
      return data.results || data
    },
    enabled: !!productId,
    retry: 1,
  })
}

export const useCreateProductQuestion = (productId: number) => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (text: string) => {
      const { data } = await api.post(ROUTES.REVIEWS.QUESTIONS, {
        product: productId,
        text,
      })
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["questions", "product", productId] })
    },
  })
}

export const useAnswerProductQuestion = (productId: number) => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ id, answer }: { id: number; answer: string }) => {
      const { data } = await api.post(ROUTES.REVIEWS.QUESTION_ANSWER(id), {
        answer,
      })
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["questions", "product", productId] })
    },
  })
}
