/**
 * Valida o semáforo de admissibilidade e o indicador de liminar com LLM real.
 *
 * REQUER: `make dev-backend` em outro terminal (consome tokens da API do LLM).
 * Configuração: playwright.llm.config.ts (timeout 90 s por teste, retries=0).
 *
 * Garantia de "zero loop": cada teste faz exatamente 1 chamada à API e
 * aguarda a resposta com hard-timeout do Playwright. Se o LLM travar, o
 * teste falha em 90 s — não fica em loop. `retries: 0` elimina qualquer
 * tentativa automática de reexecução.
 *
 * Cobertura:
 *   - Semáforo de admissibilidade (GREEN / RED / YELLOW) — assertiva principal
 *   - Indicador de liminar no resumo — quando expect_liminar não é null
 */

import * as fs from "fs";
import * as path from "path";

import { expect, test } from "@playwright/test";

const SYNTHETIC_DIR = path.resolve(__dirname, "../../../backend/data/synthetic");

type Label = {
  category: string;
  is_malicious: boolean;
  expected_verdict: "PASS" | "WARN" | "BLOCK";
  rito: "CIVEL" | "TRABALHISTA";
  expect_semaforo: string | null;
  expect_requer_emenda: boolean | null;
  expect_liminar: boolean | null;
};

const LABELS_PATH = path.join(SYNTHETIC_DIR, "labels.json");
const labels: Record<string, Label> = fs.existsSync(LABELS_PATH)
  ? (JSON.parse(fs.readFileSync(LABELS_PATH, "utf-8")) as Record<string, Label>)
  : {};

// Mapeamento pt-BR → valores da API (AdmissibilityStatus em types.ts)
const SEMAFORO_TO_STATUS: Record<string, string> = {
  VERDE: "GREEN",
  VERMELHO: "RED",
  AMARELO: "YELLOW",
};

// Apenas cenários com expectativa de semáforo definida e que não são maliciosos.
// Injeções não chegam à admissibilidade (firewall bloqueia antes).
const LLM_SCENARIOS = Object.entries(labels).filter(
  ([, l]) => l.expect_semaforo !== null && !l.is_malicious
);

if (LLM_SCENARIOS.length === 0) {
  test("corpus ausente ou sem cenários com semáforo definido", async () => {
    throw new Error("labels.json não encontrado ou vazio. Execute: make synthetic");
  });
}

for (const [filename, label] of LLM_SCENARIOS) {
  const apiStatus = SEMAFORO_TO_STATUS[label.expect_semaforo!];

  test(`[${label.category}] ${filename} → admissibilidade ${label.expect_semaforo}`, async ({ page }) => {
    const pdfPath = path.join(SYNTHETIC_DIR, filename);
    if (!fs.existsSync(pdfPath)) {
      test.skip(true, `PDF ausente: ${filename}. Execute: make synthetic`);
      return;
    }

    await page.goto("/");

    if (label.rito === "TRABALHISTA") {
      await page.getByRole("button", { name: "Trabalhista" }).click();
    }

    await page.setInputFiles("input[type=file]", pdfPath);
    await page.locator('[data-testid="analyze-btn"]').click();

    // Aguarda o resultado — timeout hard de 90 s (configurado no playwright.llm.config.ts).
    // Se o LLM não responder em tempo, o teste falha aqui; não entra em loop.
    await expect(page.locator('[data-testid="analysis-result"]')).toBeVisible();

    // O painel de admissibilidade deve estar visível (cenário não é injeção nem BLOCK).
    const admPanel = page.locator('[data-testid="admissibility-panel"]');
    await expect(admPanel).toBeVisible();

    // Semáforo: valida via data-status no próprio painel.
    await expect(page.locator(`[data-testid="admissibility-panel"][data-status="${apiStatus}"]`))
      .toBeVisible();

    // Indicador de liminar no resumo — apenas quando a expectativa é explícita (não null).
    const injunctionBadge = page.locator('[data-testid="summary-has-injunction"]');
    if (label.expect_liminar === true) {
      await expect(injunctionBadge).toBeVisible();
    } else if (label.expect_liminar === false) {
      await expect(injunctionBadge).not.toBeVisible();
    }
    // label.expect_liminar === null → não há expectativa definida; assertion omitida
  });
}
