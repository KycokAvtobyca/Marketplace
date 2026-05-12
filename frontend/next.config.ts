import path from "path"
import type { NextConfig } from "next"

const nextConfig: NextConfig = {
  sassOptions: {
    includePaths: [path.join(process.cwd(), "src")],
  },
  turbopack: {
    rules: {
      "*.svg": {
        loaders: ["@svgr/webpack"],
        as: "*.js",
      },
    },
  },
  // // В новых версиях параметр может находиться здесь:
  // devIndicators: {
  //   appIsrStatus: true,
  // },

  allowedDevOrigins: [
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    "http://0.0.0.0:3000",
  ],
}
// Временно используем any, так как типы в 16.1.7 могут отставать от движка

export default nextConfig
