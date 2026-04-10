export const Overlay: React.FC = () => {
  return (
    <div
      aria-hidden="true"
      className="fixed bg-obsidian/40 backdrop-blur-[2px] z-20 cursor-pointer transition-all duration-300 inset-0 w-full h-full"
    ></div>
  )
}
