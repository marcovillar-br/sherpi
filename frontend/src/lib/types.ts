// Tipos espelhando o contrato da API do SHERPI.

export type RiskVerdict = "PASS" | "WARN" | "BLOCK";
export type Semaforo = "VERDE" | "AMARELO" | "VERMELHO";
export type Polo = "ATIVO" | "PASSIVO";
export type TipoPedido = "PRINCIPAL" | "LIMINAR" | "SUBSIDIARIO";
export type MetodoCheck = "DETERMINISTICO" | "SEMANTICO";
export type Rito = "CIVEL" | "TRABALHISTA";
export type ReviewDecision = "ACEITAR" | "REJEITAR" | "CORRIGIR";

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
  nome: string;
  documento: string | null;
  polo: Polo;
  endereco: string | null;
}

export interface Pedido {
  descricao: string;
  tipo: TipoPedido;
  valor: string | null;
}

export interface PetitionSummary {
  partes: Parte[];
  fato_gerador: string;
  fundamentacao: string;
  pedidos: Pedido[];
  tem_liminar: boolean;
  valor_causa: string | null;
  documentos_mencionados: string[];
}

export interface ChecklistItem {
  requisito: string;
  presente: boolean;
  metodo: MetodoCheck;
  evidencia: string | null;
  detalhe: string | null;
}

export interface AdmissibilityReport {
  itens: ChecklistItem[];
  semaforo: Semaforo;
  requer_emenda: boolean;
}

export interface TpuSuggestion {
  code: string;
  label: string;
  confidence: number;
  anchor: string | null;
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
