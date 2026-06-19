// Tipos espelhando o contrato da API do SHERPI.

export type RiskVerdict = "PASS" | "WARN" | "BLOCK";
export type AdmissibilityStatus = "GREEN" | "YELLOW" | "RED";
export type Polo = "ACTIVE" | "PASSIVE";
export type ClaimType = "MAIN" | "INJUNCTION" | "SUBSIDIARY";
export type CheckMethod = "DETERMINISTIC" | "SEMANTIC";
export type Rito = "CIVEL" | "TRABALHISTA";
export type ReviewDecision = "ACCEPT" | "REJECT" | "AMEND";

export interface Anomaly {
  type: string;
  severity: string;
  detail: string;
  page: number | null;
  evidence: string | null;
}

export interface ForensicsReport {
  verdict: RiskVerdict;
  risk_score: number;
  anomalies: Anomaly[];
}

export interface Parte {
  name: string;
  document: string | null;
  pole: Polo;
  address: string | null;
}

export interface Pedido {
  description: string;
  type: ClaimType;
  amount: string | null;
}

export interface PetitionSummary {
  court: string | null;
  parties: Parte[];
  facts: string;
  legal_basis: string;
  claims: Pedido[];
  has_injunction: boolean;
  claim_amount: string | null;
  requests_evidence: boolean;
  hearing_option: boolean | null;
  cited_documents: string[];
}

export interface ChecklistItem {
  requirement: string;
  present: boolean;
  method: CheckMethod;
  evidence: string | null;
  detail: string | null;
}

export interface AdmissibilityReport {
  items: ChecklistItem[];
  status: AdmissibilityStatus;
  requires_amendment: boolean;
}

export interface TpuSuggestion {
  tpu_code: string;
  description: string;
  confidence: number;
  anchor_excerpt: string;
}

export interface AnalysisResult {
  forensics: ForensicsReport;
  summary: PetitionSummary | null;
  admissibility: AdmissibilityReport | null;
  tpu_suggestions: TpuSuggestion[] | null;
  rito: Rito;
}

export interface AnalyzeResponse {
  id: string;
  result: AnalysisResult;
}

export interface AuditEvent {
  id: string;
  analysis_id: string;
  user_id: string;
  decision: ReviewDecision;
  comment: string | null;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}
