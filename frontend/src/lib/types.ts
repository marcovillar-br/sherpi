// Tipos espelhando o contrato da API do SHERPI (/v1/analyze).

export type RiskVerdict = "PASS" | "WARN" | "BLOCK";
export type Semaforo = "VERDE" | "AMARELO" | "VERMELHO";
export type Polo = "ATIVO" | "PASSIVO";
export type TipoPedido = "PRINCIPAL" | "LIMINAR" | "SUBSIDIARIO";
export type MetodoCheck = "DETERMINISTICO" | "SEMANTICO";

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

export interface AnalysisResult {
  forensics: ForensicsReport;
  summary: PetitionSummary | null;
  admissibility: AdmissibilityReport | null;
}

export interface AnalyzeResponse {
  id: string;
  result: AnalysisResult;
}
