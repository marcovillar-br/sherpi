/**
 * Validação automática de todos os cenários sintéticos contra o firewall.
 *
 * O que é testado: veredito do firewall (PASS / WARN / BLOCK) — determinístico, sem LLM.
 * O que NÃO é testado: conteúdo do resumo ou admissibilidade (requer LLM real).
 *
 * Pré-requisito: backend rodando com SHERPI_LLM_BACKEND=fake (make dev-backend-fake).
 * A admissibilidade com FakeProvider é não-determinística — intencionalmente ignorada aqui.
 */

import * as fs from "fs";
import * as path from "path";

import { expect, test } from "@playwright/test";

const SYNTHETIC_DIR = path.resolve(__dirname, "../../../backend/data/synthetic");
const LABELS_PATH = path.join(SYNTHETIC_DIR, "labels.json");

type Label = {
  category: string;
  description: string;
  is_malicious: boolean;
  expected_verdict: "PASS" | "WARN" | "BLOCK";
  rito: "CIVEL" | "TRABALHISTA";
};

const labels: Record<string, Label> = fs.existsSync(LABELS_PATH)
  ? (JSON.parse(fs.readFileSync(LABELS_PATH, "utf-8")) as Record<string, Label>)
  : {};

if (Object.keys(labels).length === 0) {
  test("corpus sintético ausente", async () => {
    throw new Error("labels.json não encontrado. Execute: make synthetic");
  });
}

for (const [filename, label] of Object.entries(labels)) {
  test(`[${label.category}] ${filename} → firewall ${label.expected_verdict}`, async ({ page }) => {
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

    // Aguarda o resultado aparecer — falha em 30 s sem retry (zero risco de loop infinito)
    await expect(page.locator('[data-testid="analysis-result"]')).toBeVisible({ timeout: 30_000 });

    // Veredito do firewall é determinístico: não depende do LLM
    await expect(page.locator(`[data-testid="forensics-${label.expected_verdict}"]`)).toBeVisible();
  });
}
