"use client"

import React, { useCallback, useState } from "react"
import Head from "next/head"
import { useParams, useRouter } from "next/navigation"
import { useQueryClient } from "@tanstack/react-query"
import { useAddToCart } from "@/entities/cart/api/useCart"
import { useProduct } from "@/entities/products/api/useProduct"
import { useProfile } from "@/entities/user/api/useProfile"
import { useAuthWindowStore } from "@/entities/authWindow"
import {
  useAnswerProductQuestion,
  useCreateProductQuestion,
  useCreateReview,
  useDeleteReview,
  useProductQuestions,
  useProductReviews,
  useUpdateReview,
  useVoteReview,
} from "@/entities/reviews"

type ApiError = {
  response?: { data?: Record<string, string[] | string> }
}

const formatPrice = (value: number) =>
  value.toLocaleString("ru-RU", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })

export default function ProductPage() {
  const params = useParams()
  const router = useRouter()
  const id = Number(params?.id)
  const { data: product, isLoading } = useProduct(id)
  const { data: reviews = [] } = useProductReviews(id)
  const { data: questions = [] } = useProductQuestions(id)
  const { mutate: createReview, isPending: isCreatingReview } = useCreateReview(id)
  const { mutate: updateReview, isPending: isUpdatingReview } = useUpdateReview(id)
  const { mutate: deleteReview, isPending: isDeletingReview } = useDeleteReview(id)
  const { mutate: voteReview, isPending: isVotingReview } = useVoteReview(id)
  const { mutate: createQuestion, isPending: isCreatingQuestion } =
    useCreateProductQuestion(id)
  const { mutate: answerQuestion, isPending: isAnsweringQuestion } =
    useAnswerProductQuestion(id)
  const { mutate: addToCart, isPending: isAdding } = useAddToCart()
  const queryClient = useQueryClient()
  const { data: profile } = useProfile()
  const toggleAuthWindow = useAuthWindowStore((s) => s.toggle)

  const [selectedVariant, setSelectedVariant] = useState<number | null>(null)
  const [currentImageIndex, setCurrentImageIndex] = useState(0)
  const [touchStart, setTouchStart] = useState<number | null>(null)
  const [quantity, setQuantity] = useState(1)
  const [reviewRating, setReviewRating] = useState(5)
  const [reviewText, setReviewText] = useState("")
  const [reviewMessage, setReviewMessage] = useState("")
  const [editingReviewId, setEditingReviewId] = useState<number | null>(null)
  const [questionText, setQuestionText] = useState("")
  const [questionMessage, setQuestionMessage] = useState("")
  const [answerDrafts, setAnswerDrafts] = useState<Record<number, string>>({})

  const mainVariant =
    product?.variants.find((variant) => variant.is_main) || product?.variants[0]
  const activeVariant =
    product?.variants.find((variant) => variant.id === selectedVariant) ||
    mainVariant
  const allImages = activeVariant?.images || []
  const currentImage = allImages[currentImageIndex]
  const averageRating =
    reviews.length > 0
      ? reviews.reduce((sum, review) => sum + review.rating, 0) / reviews.length
      : null
  const canAnswerQuestions =
    !!profile &&
    !!product?.shop &&
    (profile.is_superuser || profile.id === product.shop.owner)

  const handlePrevImage = useCallback(() => {
    setCurrentImageIndex((prev) => (prev > 0 ? prev - 1 : allImages.length - 1))
  }, [allImages.length])

  const handleNextImage = useCallback(() => {
    setCurrentImageIndex((prev) => (prev < allImages.length - 1 ? prev + 1 : 0))
  }, [allImages.length])

  const handleTouchStart = (event: React.TouchEvent) => {
    setTouchStart(event.touches[0].clientX)
  }

  const handleTouchEnd = (event: React.TouchEvent) => {
    if (touchStart === null) return
    const diff = touchStart - event.changedTouches[0].clientX
    if (Math.abs(diff) > 50) {
      if (diff > 0) handleNextImage()
      else handlePrevImage()
    }
    setTouchStart(null)
  }

  const handleMouseDown = (event: React.MouseEvent) => {
    setTouchStart(event.clientX)
  }

  const handleMouseUp = (event: React.MouseEvent) => {
    if (touchStart === null) return
    const diff = touchStart - event.clientX
    if (Math.abs(diff) > 50) {
      if (diff > 0) handleNextImage()
      else handlePrevImage()
    }
    setTouchStart(null)
  }

  const handleAddToCart = () => {
    if (!activeVariant) return
    if (!profile) {
      toggleAuthWindow()
      return
    }
    addToCart(
      { product_variant_id: activeVariant.id, quantity },
      {
        onSuccess: () => {
          queryClient.invalidateQueries({ queryKey: ["cart"] })
        },
      },
    )
  }

  const handleReviewSubmit = (event: React.FormEvent) => {
    event.preventDefault()
    setReviewMessage("")
    if (!profile) {
      toggleAuthWindow()
      return
    }
    if (!activeVariant) return

    const handlers = {
      onSuccess: () => {
        setReviewText("")
        setReviewRating(5)
        setEditingReviewId(null)
        setReviewMessage("Отзыв отправлен на модерацию.")
      },
      onError: (error: unknown) => {
        const data = (error as ApiError).response?.data
        setReviewMessage(
          String(
            data?.product_variant?.[0] ||
              data?.description?.[0] ||
              data?.non_field_errors?.[0] ||
              data?.detail ||
              "Не удалось отправить отзыв. Отзыв можно оставить после завершенного заказа.",
          ),
        )
      },
    }

    if (editingReviewId) {
      updateReview(
        { id: editingReviewId, rating: reviewRating, description: reviewText },
        handlers,
      )
      return
    }

    createReview(
      {
        product_variant: activeVariant.id,
        rating: reviewRating,
        description: reviewText,
      },
      handlers,
    )
  }

  const handleDeleteReview = (reviewId: number) => {
    if (!window.confirm("Удалить отзыв?")) return
    deleteReview(reviewId, {
      onSuccess: () => {
        setReviewMessage("Отзыв удален.")
        if (editingReviewId === reviewId) {
          setEditingReviewId(null)
          setReviewText("")
          setReviewRating(5)
        }
      },
    })
  }

  const handleQuestionSubmit = (event: React.FormEvent) => {
    event.preventDefault()
    setQuestionMessage("")
    if (!profile) {
      toggleAuthWindow()
      return
    }
    createQuestion(questionText, {
      onSuccess: () => {
        setQuestionText("")
        setQuestionMessage("Вопрос отправлен продавцу.")
      },
      onError: () => {
        setQuestionMessage("Не удалось отправить вопрос.")
      },
    })
  }

  if (isLoading) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-12 text-center animate-pulse sm:p-12">
        Загрузка товара...
      </div>
    )
  }

  if (!product) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-12 text-center sm:p-12">
        <h2 className="text-xl font-bold">Товар не найден</h2>
        <button
          onClick={() => router.push("/")}
          className="mt-4 px-6 py-2 bg-brand-main text-white rounded-xl"
        >
          На главную
        </button>
      </div>
    )
  }

  return (
    <>
      <Head>
        <title>{product.name} — Floppi</title>
        <meta
          name="description"
          content={
            product.description?.slice(0, 160) ||
            `${product.name} в маркетплейсе Floppi`
          }
        />
      </Head>
      <main className="mx-auto max-w-5xl p-3 sm:p-6">
        <div className="grid grid-cols-1 gap-5 lg:grid-cols-[minmax(0,1fr)_minmax(320px,1fr)] lg:gap-8">
          <div className="space-y-4">
            <div
              className="relative aspect-square select-none overflow-hidden rounded-2xl bg-slate-100 sm:aspect-[3/4]"
              onTouchStart={handleTouchStart}
              onTouchEnd={handleTouchEnd}
              onMouseDown={handleMouseDown}
              onMouseUp={handleMouseUp}
            >
              {currentImage ? (
                <img
                  src={currentImage.image}
                  alt={product.name}
                  className="w-full h-full object-contain"
                  draggable={false}
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-slate-400">
                  Нет изображения
                </div>
              )}

              {allImages.length > 1 && (
                <>
                  <button
                    onClick={handlePrevImage}
                    className="absolute left-2 top-1/2 -translate-y-1/2 w-10 h-10 bg-white/80 backdrop-blur rounded-full flex items-center justify-center shadow-lg hover:bg-white transition-colors"
                  >
                    {"<"}
                  </button>
                  <button
                    onClick={handleNextImage}
                    className="absolute right-2 top-1/2 -translate-y-1/2 w-10 h-10 bg-white/80 backdrop-blur rounded-full flex items-center justify-center shadow-lg hover:bg-white transition-colors"
                  >
                    {">"}
                  </button>
                </>
              )}
            </div>

            {allImages.length > 1 && (
              <div className="flex gap-2 overflow-auto pb-1">
                {allImages.map((image, index) => (
                  <button
                    key={image.id}
                    onClick={() => setCurrentImageIndex(index)}
                    className={`shrink-0 w-16 h-16 rounded-xl overflow-hidden border-2 transition-colors ${
                      index === currentImageIndex
                        ? "border-brand-main"
                        : "border-transparent"
                    }`}
                  >
                    <img
                      src={image.image}
                      alt=""
                      className="w-full h-full object-contain"
                    />
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="min-w-0 space-y-6">
            <div>
              {product.brand && (
                <p className="text-sm text-slate-500 mb-1">
                  {product.brand.name}
                </p>
              )}
              <h1 className="text-2xl sm:text-3xl font-bold">{product.name}</h1>
              <div className="mt-2 flex items-center gap-2 text-sm text-slate-500">
                <span className="text-yellow-500">★</span>
                <span>
                  {averageRating ? averageRating.toFixed(1) : "Нет оценок"}
                </span>
                <span>·</span>
                <span>{reviews.length} отзывов</span>
              </div>
              {product.category && (
                <p className="text-sm text-slate-400 mt-1">
                  {product.category.name}
                </p>
              )}
            </div>

            {activeVariant && (
              <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
                <span className="text-2xl font-black text-brand-main sm:text-3xl">
                  {formatPrice(Number(activeVariant.final_price))} ₽
                </span>
                {activeVariant.has_discount && (
                  <span className="text-lg text-slate-400 line-through">
                    {formatPrice(
                      Number(
                        activeVariant.final_price /
                          (1 - (activeVariant.discount_pct || 0) / 100),
                      ),
                    )}{" "}
                    ₽
                  </span>
                )}
              </div>
            )}

            {product.variants.length > 1 && (
              <div>
                <p className="text-sm font-medium text-slate-600 mb-2">
                  Варианты:
                </p>
                <div className="flex flex-wrap gap-2">
                  {product.variants.map((variant) => (
                    <button
                      key={variant.id}
                      onClick={() => {
                        setSelectedVariant(variant.id)
                        setCurrentImageIndex(0)
                      }}
                      className={`px-3 py-1.5 rounded-lg text-sm font-medium border transition-all ${
                        variant.id === activeVariant?.id
                          ? "bg-brand-main text-white border-brand-main"
                          : "bg-white text-slate-700 border-slate-200 hover:border-brand-main"
                      }`}
                    >
                      {variant.attribute_values.map((av) => av.name).join(", ") ||
                        variant.sku}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {activeVariant && activeVariant.attribute_values.length > 0 && (
              <div className="space-y-1">
                <p className="text-sm font-medium text-slate-600">
                  Характеристики:
                </p>
                {activeVariant.attribute_values.map((av) => (
                  <div
                    key={av.id}
                    className="flex justify-between text-sm py-1 border-b border-slate-50"
                  >
                    <span className="text-slate-500">{av.name}</span>
                  </div>
                ))}
              </div>
            )}

            <div className="flex items-center gap-2">
              <span
                className={`w-2 h-2 rounded-full ${
                  activeVariant && activeVariant.stock > 0
                    ? "bg-green-500"
                    : "bg-red-500"
                }`}
              />
              <span className="text-sm">
                {activeVariant && activeVariant.stock > 0
                  ? `В наличии: ${activeVariant.stock} шт.`
                  : "Нет в наличии"}
              </span>
            </div>

            <div className="flex flex-col gap-3 min-[420px]:flex-row">
              <div className="flex w-full items-center justify-between rounded-xl border border-slate-200 min-[420px]:w-auto">
                <button
                  onClick={() => setQuantity(Math.max(1, quantity - 1))}
                  className="px-3 py-2 text-lg font-medium hover:bg-slate-50"
                >
                  −
                </button>
                <input
                  type="number"
                  min={1}
                  max={activeVariant?.stock || 1}
                  value={quantity}
                  onChange={(event) => {
                    const value = Number(event.target.value)
                    setQuantity(
                      Math.max(
                        1,
                        Math.min(activeVariant?.stock || 1, Number.isNaN(value) ? 1 : value),
                      ),
                    )
                  }}
                  className="w-14 px-1 py-2 text-center text-sm font-bold outline-none"
                />
                <button
                  onClick={() =>
                    setQuantity(
                      Math.min(activeVariant ? activeVariant.stock : 1, quantity + 1),
                    )
                  }
                  className="px-3 py-2 text-lg font-medium hover:bg-slate-50"
                >
                  +
                </button>
              </div>
              <button
                onClick={handleAddToCart}
                disabled={isAdding || !activeVariant || activeVariant.stock <= 0}
                className="w-full rounded-xl bg-brand-main py-3 font-bold text-white shadow-lg shadow-brand-main/20 transition-all hover:brightness-110 active:scale-[0.98] disabled:opacity-50 min-[420px]:flex-1"
              >
                {isAdding ? "Добавление..." : "В корзину"}
              </button>
            </div>

            {product.description && (
              <div>
                <p className="text-sm font-medium text-slate-600 mb-1">
                  Описание:
                </p>
                <p className="text-sm text-slate-500 whitespace-pre-line">
                  {product.description}
                </p>
              </div>
            )}

            {product.shop && (
              <div className="p-3 bg-slate-50 rounded-xl">
                <p className="text-xs text-slate-400">Продавец</p>
                <p className="font-medium">{product.shop.name}</p>
              </div>
            )}
          </div>
        </div>

        <section className="mt-10 grid grid-cols-1 gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(280px,360px)]">
          <div className="min-w-0 space-y-4">
            <h2 className="text-xl font-bold">Вопросы о товаре</h2>
            {questions.length > 0 ? (
              questions.map((question) => (
                <article
                  key={question.id}
                  className="rounded-2xl border border-slate-100 bg-white p-4 shadow-sm"
                >
                  <p className="text-xs text-slate-400">
                    {question.author_name} ·{" "}
                    {new Date(question.date_time_create).toLocaleDateString("ru-RU")}
                  </p>
                  <p className="mt-2 text-sm text-slate-700">{question.text}</p>
                  {question.answer ? (
                    <div className="mt-3 rounded-xl bg-slate-50 p-3 text-sm">
                      <p className="font-semibold text-slate-900">
                        {question.answered_by_name || "Продавец"}
                      </p>
                      <p className="mt-1 text-slate-600">{question.answer}</p>
                    </div>
                  ) : (
                    <p className="mt-3 text-xs text-slate-400">
                      Продавец еще не ответил.
                    </p>
                  )}
                  {canAnswerQuestions && !question.answer && (
                    <div className="mt-3 flex flex-col gap-2 min-[520px]:flex-row">
                      <input
                        value={answerDrafts[question.id] || ""}
                        onChange={(event) =>
                          setAnswerDrafts((prev) => ({
                            ...prev,
                            [question.id]: event.target.value,
                          }))
                        }
                        placeholder="Ответ продавца"
                        className="min-w-0 flex-1 rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-brand-main"
                      />
                      <button
                        onClick={() =>
                          answerQuestion({
                            id: question.id,
                            answer: answerDrafts[question.id] || "",
                          })
                        }
                        disabled={
                          isAnsweringQuestion ||
                          (answerDrafts[question.id] || "").trim().length < 2
                        }
                        className="rounded-xl bg-brand-main px-4 py-2 text-sm font-bold text-white disabled:opacity-50"
                      >
                        Ответить
                      </button>
                    </div>
                  )}
                </article>
              ))
            ) : (
              <p className="rounded-2xl border border-slate-100 bg-white p-4 text-sm text-slate-500">
                Вопросов пока нет.
              </p>
            )}
          </div>

          <form
            onSubmit={handleQuestionSubmit}
            className="min-w-0 self-start rounded-2xl border border-slate-100 bg-white p-4 shadow-sm"
          >
            <h3 className="font-bold text-slate-900">Задать вопрос</h3>
            <textarea
              value={questionText}
              onChange={(event) => setQuestionText(event.target.value)}
              rows={5}
              minLength={5}
              className="mt-3 w-full resize-none rounded-xl border border-slate-200 px-3 py-2 outline-none focus:border-brand-main"
              placeholder="Напишите вопрос продавцу"
            />
            {questionMessage && (
              <p className="mt-2 text-xs text-slate-500">{questionMessage}</p>
            )}
            <button
              type="submit"
              disabled={isCreatingQuestion || questionText.trim().length < 5}
              className="mt-4 w-full rounded-xl bg-brand-main py-3 text-sm font-bold text-white transition hover:brightness-110 disabled:opacity-50"
            >
              {isCreatingQuestion ? "Отправка..." : "Отправить вопрос"}
            </button>
          </form>
        </section>

        <section className="mt-10 grid grid-cols-1 gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(280px,360px)]">
          <div className="min-w-0 space-y-4">
            <h2 className="text-xl font-bold">Отзывы и оценки</h2>
            {reviews.length > 0 ? (
              reviews.map((review) => {
                const isOwner = profile?.id === review.user_id
                return (
                  <article
                    key={review.id}
                    className="rounded-2xl border border-slate-100 bg-white p-4 shadow-sm"
                  >
                    <div className="flex flex-col gap-2 min-[420px]:flex-row min-[420px]:items-center min-[420px]:justify-between">
                      <div>
                        <p className="font-semibold text-slate-900">
                          {review.author_name}
                        </p>
                        <p className="text-xs text-slate-400">
                          {new Date(review.date_time_create).toLocaleDateString(
                            "ru-RU",
                          )}
                          {review.status !== "APPROVED"
                            ? " · на модерации"
                            : ""}
                        </p>
                      </div>
                      <p className="font-bold text-yellow-500">★ {review.rating}</p>
                    </div>
                    <p className="mt-3 whitespace-pre-line text-sm text-slate-600">
                      {review.description}
                    </p>
                    <div className="mt-3 flex flex-wrap items-center gap-2 text-xs">
                      <button
                        onClick={() =>
                          voteReview({ id: review.id, value: "USEFUL" })
                        }
                        disabled={isVotingReview || isOwner || !profile}
                        className={`rounded-lg border px-3 py-1 ${
                          review.current_user_vote === "USEFUL"
                            ? "border-brand-main text-brand-main"
                            : "border-slate-200 text-slate-500"
                        } disabled:opacity-50`}
                      >
                        Полезно: {review.useful_count}
                      </button>
                      <button
                        onClick={() =>
                          voteReview({ id: review.id, value: "UNUSEFUL" })
                        }
                        disabled={isVotingReview || isOwner || !profile}
                        className={`rounded-lg border px-3 py-1 ${
                          review.current_user_vote === "UNUSEFUL"
                            ? "border-brand-main text-brand-main"
                            : "border-slate-200 text-slate-500"
                        } disabled:opacity-50`}
                      >
                        Неполезно: {review.unuseful_count}
                      </button>
                      {isOwner && (
                        <>
                          <button
                            onClick={() => {
                              setEditingReviewId(review.id)
                              setReviewRating(review.rating)
                              setReviewText(review.description)
                              setReviewMessage(
                                "После редактирования отзыв снова попадет на модерацию.",
                              )
                            }}
                            className="text-brand-main hover:underline min-[520px]:ml-auto"
                          >
                            Редактировать
                          </button>
                          <button
                            onClick={() => handleDeleteReview(review.id)}
                            disabled={isDeletingReview}
                            className="text-red-600 hover:underline disabled:opacity-50"
                          >
                            Удалить
                          </button>
                        </>
                      )}
                    </div>
                  </article>
                )
              })
            ) : (
              <p className="rounded-2xl border border-slate-100 bg-white p-4 text-sm text-slate-500">
                Пока нет одобренных отзывов.
              </p>
            )}
          </div>

          <form
            onSubmit={handleReviewSubmit}
            className="min-w-0 self-start rounded-2xl border border-slate-100 bg-white p-4 shadow-sm"
          >
            <h3 className="font-bold text-slate-900">
              {editingReviewId ? "Редактировать отзыв" : "Оставить отзыв"}
            </h3>
            <p className="mt-1 text-xs text-slate-500">
              Отзыв можно оставить после завершенного заказа. После отправки он
              попадет на модерацию.
            </p>
            <label className="mt-4 block text-sm font-medium text-slate-600">
              Оценка
            </label>
            <select
              value={reviewRating}
              onChange={(event) => setReviewRating(Number(event.target.value))}
              className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 outline-none focus:border-brand-main"
            >
              {[5, 4, 3, 2, 1].map((rating) => (
                <option key={rating} value={rating}>
                  {rating}
                </option>
              ))}
            </select>
            <label className="mt-4 block text-sm font-medium text-slate-600">
              Текст отзыва
            </label>
            <textarea
              value={reviewText}
              onChange={(event) => setReviewText(event.target.value)}
              rows={5}
              minLength={10}
              className="mt-1 w-full resize-none rounded-xl border border-slate-200 px-3 py-2 outline-none focus:border-brand-main"
              placeholder="Расскажите, что понравилось или что можно улучшить"
            />
            {reviewMessage && (
              <p className="mt-2 text-xs text-slate-500">{reviewMessage}</p>
            )}
            <button
              type="submit"
              disabled={
                isCreatingReview ||
                isUpdatingReview ||
                reviewText.trim().length < 10
              }
              className="mt-4 w-full rounded-xl bg-brand-main py-3 text-sm font-bold text-white transition hover:brightness-110 disabled:opacity-50"
            >
              {isCreatingReview || isUpdatingReview
                ? "Отправка..."
                : editingReviewId
                  ? "Сохранить и отправить"
                  : "Отправить отзыв"}
            </button>
            {editingReviewId && (
              <button
                type="button"
                onClick={() => {
                  setEditingReviewId(null)
                  setReviewText("")
                  setReviewRating(5)
                  setReviewMessage("")
                }}
                className="mt-2 w-full rounded-xl border border-slate-200 py-3 text-sm font-bold text-slate-600"
              >
                Отменить редактирование
              </button>
            )}
          </form>
        </section>
      </main>
    </>
  )
}
