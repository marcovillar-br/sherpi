// Rótulos pt-BR para os valores de enum vindos da API (que são en-US).
// Centralizados aqui para manter toda a interface em português.

import type {
  AdmissibilityStatus,
  ClaimType,
  Polo,
  ReviewDecision,
  RiskVerdict,
  Rito,
} from "./types";

export const REVIEW_DECISION_LABEL: Record<ReviewDecision, string> = {
  ACCEPT: "Aceito",
  AMEND: "Corrigir",
  REJECT: "Rejeitado",
};

export const VERDICT_LABEL: Record<RiskVerdict, string> = {
  PASS: "Íntegro",
  WARN: "Atenção",
  BLOCK: "Bloqueado",
};

export const ADMISSIBILITY_LABEL: Record<AdmissibilityStatus, string> = {
  GREEN: "Verde",
  YELLOW: "Amarelo",
  RED: "Vermelho",
};

export const RITO_LABEL: Record<Rito, string> = {
  CIVEL: "Cível",
  TRABALHISTA: "Trabalhista",
};

export const POLO_LABEL: Record<Polo, string> = {
  ACTIVE: "ativo",
  PASSIVE: "passivo",
};

export const CLAIM_TYPE_LABEL: Record<ClaimType, string> = {
  MAIN: "principal",
  INJUNCTION: "liminar",
  SUBSIDIARY: "subsidiário",
};

// Tipados como string: a API entrega esses campos como texto livre.
export const CHECK_METHOD_LABEL: Record<string, string> = {
  DETERMINISTIC: "determinístico",
  SEMANTIC: "semântico",
};

export const SEVERITY_LABEL: Record<string, string> = {
  LOW: "Baixa",
  MEDIUM: "Média",
  HIGH: "Alta",
  CRITICAL: "Crítica",
};

export const ANOMALY_TYPE_LABEL: Record<string, string> = {
  WHITE_ON_WHITE: "Texto na cor do fundo",
  TINY_FONT: "Fonte microscópica",
  OFF_CROPBOX: "Texto fora da área visível",
  ZERO_WIDTH_UNICODE: "Caracteres invisíveis",
  HIDDEN_OCG_LAYER: "Camada oculta",
  ACTUALTEXT_DIVERGENCE: "Divergência de /ActualText",
  SUSPICIOUS_METADATA: "Metadados suspeitos",
  INJECTION_KEYWORDS: "Comando oculto à IA",
};
