// T - это тип стора
type ZustandSet<T> = (
  next: (state: T) => void, // Immer позволяет не возвращать объект
  shouldReplace?: false,
  actionName?: string, // Добавляется благодаря devtools
) => void

export const genericSetAction = <T extends object>(
  set: ZustandSet<T>,
  stateObj: keyof T,
  newValue: T[keyof T],
  action?: string,
  shouldReplace?: false,
) => {
  set(
    (state) => {
      if (!(stateObj in state)) {
        throw new Error(`Свойство ${String(stateObj)} не найдено в сторе`)
      }

      //   if (state[stateObj] !== newValue) {
      state[stateObj] = newValue
      //   }
    },
    shouldReplace,
    action,
  )
}
