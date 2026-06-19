import { defineConfig, devices } from "@playwright/test";

// Config para testes que requerem LLM real.
// Pré-requisito: `make dev-backend` rodando em outro terminal.
// Custo: ~1 chamada ao LLM por cenário (8 cenários com expect_semaforo definido).
export default defineConfig({
  testDir: "./tests/e2e",
  timeout: 90_000,   // LLM pode demorar; falha em 90 s — sem loop possível
  retries: 0,        // zero retry: cada teste faz 1 chamada e retorna sucesso ou falha
  workers: 1,        // serial: evita saturar a API do LLM

  reporter: [["list"], ["html", { open: "never", outputFolder: "playwright-report-llm" }]],

  use: {
    baseURL: "http://localhost:3000",
    headless: true,
    screenshot: "only-on-failure",
    video: "off",
  },

  projects: [
    {
      name: "setup",
      testMatch: /auth\.setup\.ts/,
    },
    {
      name: "e2e-llm",
      use: {
        ...devices["Desktop Chrome"],
        storageState: "playwright/.auth/user.json",
      },
      dependencies: ["setup"],
      testMatch: /admissibility\.spec\.ts/,
    },
  ],

  webServer: {
    command: "npm run dev",
    url: "http://localhost:3000",
    reuseExistingServer: true,
    timeout: 30_000,
  },
});
