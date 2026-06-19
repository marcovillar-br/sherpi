import * as fs from "fs";
import * as path from "path";

import { test as setup } from "@playwright/test";

const AUTH_FILE = path.join(__dirname, "../../playwright/.auth/user.json");

setup("autenticar usuário de demo", async ({ page }) => {
  fs.mkdirSync(path.dirname(AUTH_FILE), { recursive: true });

  await page.goto("/login");
  await page.fill("#email", process.env.SHERPI_E2E_EMAIL ?? "gabinete@sherpi.local");
  await page.fill("#password", process.env.SHERPI_E2E_PASSWORD ?? "6aeda6bf73531cd01c2e449c");
  await page.click('button[type=submit]');

  // Aguarda redirect para "/" — sem setTimeout, sem loop, falha em 10 s se não redirecionar
  await page.waitForURL("/", { timeout: 10_000 });

  await page.context().storageState({ path: AUTH_FILE });
});
