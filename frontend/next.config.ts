import path from "path"
import type { NextConfig } from "next"

const nextConfig: NextConfig = {
  sassOptions: {
    // Это говорит Sass: "Если не нашел файл, загляни в папку src"
    includePaths: [path.join(process.cwd(), "src")],
  },
}

export default nextConfig
