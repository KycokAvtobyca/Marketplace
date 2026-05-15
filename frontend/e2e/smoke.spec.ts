import { expect, test } from "@playwright/test"
import { execFileSync } from "node:child_process"
import path from "node:path"

const frontendUrl = process.env.FRONTEND_URL || "http://127.0.0.1:3000"
const backendUrl = process.env.BACKEND_URL || "http://127.0.0.1:8000"
const backendDir = path.resolve(__dirname, "../../backend")
const pythonPath = path.join(backendDir, "venv", "Scripts", "python.exe")

const createSmsCode = () => {
  const code = "123456"
  execFileSync(
    pythonPath,
    [
      "manage.py",
      "shell",
      "-c",
      `from django.utils import timezone; from users.models import SMSCode; SMSCode.objects.update_or_create(phone_number='+79642297622', defaults={'code': '${code}', 'date_time_create': timezone.now()})`,
    ],
    {
      cwd: backendDir,
      encoding: "utf8",
    },
  )
  return code
}

test.describe("marketplace smoke", () => {
  for (const route of [
    "/",
    "/catalog",
    "/cart",
    "/favorites",
    "/checkout",
    "/profile",
    "/shop/create",
  ]) {
    test(`frontend route ${route} renders`, async ({ page }) => {
      const response = await page.goto(route)

      expect(response?.status(), route).toBeLessThan(400)
      await expect(page.locator("body")).not.toBeEmpty()
      await expect(page.locator("body")).not.toContainText(/Application error|Unhandled Runtime Error/i)
    })
  }

  test("superuser can authenticate and open profile", async ({ browser, request }) => {
    const smsCode = createSmsCode()
    const tokenResponse = await request.post(`${backendUrl}/api/v1/users/auth/token/`, {
      data: {
        phone_number: "+79642297622",
        sms_code: smsCode,
        password: "qwerty123456",
      },
    })
    expect(tokenResponse.ok()).toBeTruthy()
    await expect(tokenResponse.json()).resolves.toEqual(
      expect.objectContaining({ is_superuser: true, is_staff: true }),
    )

    const cookieHeader = tokenResponse
      .headersArray()
      .filter((header) => header.name.toLowerCase() === "set-cookie")
      .map((header) => header.value.split(";")[0])
      .join("; ")

    expect(cookieHeader).toContain("access_token=")
    expect(cookieHeader).toContain("refresh_token=")

    const profileResponse = await request.get(`${backendUrl}/api/v1/users/profile/`, {
      headers: { Cookie: cookieHeader },
    })
    expect(profileResponse.ok()).toBeTruthy()
    await expect(profileResponse.json()).resolves.toEqual(
      expect.objectContaining({ phone_number: "+79642297622", is_staff: true }),
    )

    const context = await browser.newContext()
    await context.addCookies(
      cookieHeader.split("; ").map((cookie) => {
        const [name, value] = cookie.split("=")
        return {
          name,
          value,
          domain: "127.0.0.1",
          path: "/",
          httpOnly: true,
          sameSite: "Lax" as const,
        }
      }),
    )

    const page = await context.newPage()
    const response = await page.goto(`${frontendUrl}/profile`)
    expect(response?.status()).toBeLessThan(400)
    await expect(page.locator("body")).toContainText("+79642297622")
    await context.close()
  })
})
