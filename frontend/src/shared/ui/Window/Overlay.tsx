interface OverlayProps {
  className?: string
  toggleWindow?: () => void
}

export const Overlay: React.FC<OverlayProps> = ({
  className,
  toggleWindow,
}) => {
  return (
    <div
      aria-hidden="true"
      className={`${className} fixed bg-obsidian/40 backdrop-blur-[2px]\
      z-20 cursor-pointer transition-all duration-300 inset-0 w-full h-full`}
      onClick={toggleWindow}
    ></div>
  )
}
