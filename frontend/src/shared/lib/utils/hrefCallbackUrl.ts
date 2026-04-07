export const redirectToAndBack = (path: string) => {
  if (typeof window !== "undefined") {
    const currentPath = window.location.pathname
    window.location.href = `/${path}?callbackUrl=${encodeURIComponent(currentPath)}`
  }
}
