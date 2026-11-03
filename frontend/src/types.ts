export type Block = "C1" | "C2" | "C3" | "C4";
export const BLOCKS: Block[] = ["C1", "C2", "C3", "C4"];

export const BLOCK_NAMES: Record<Block, string> = {
  C1: "Normativ-huquqiy va tashkiliy",
  C2: "Texnik va operatsion himoya",
  C3: "Kiberinsidentlarni boshqarish va tiklash",
  C4: "Kibergigiyena va ijtimoiy muhandislik",
};

export const LEVELS = [
  "Kritik (Boshlang‘ich) daraja",
  "Shartli bazaviy (Kritik blok oqsagan)",
  "Bazaviy (Rivojlanayotgan) daraja",
  "Malakali (Yetarli) daraja",
  "Ekspert (Yuqori) daraja",
];

export interface User {
  id: number;
  username: string;
  full_name: string;
  role: "admin" | "officer";
  position: string;
  agency: string;
  category: string;
}

export interface SessionSummary {
  id: number;
  stage: "before" | "after" | "attestatsiya";
  stage_label: string;
  created_at: string;
  i_axk: number;
  phi: number;
  level: string;
  c: Record<Block, number>;
  duration_minutes: number;
}

export interface PlanItem {
  id: number;
  block_code: string;
  sub_code: string;
  delta_c: number;
  title: string;
  hours: number;
  deadline_days: number;
  status: string;
}

export interface SessionFull extends SessionSummary {
  verify_code: string;
  k: Record<Block, number>;
  s: Record<Block, number>;
  a: Record<Block, number>;
  sub_scores: Record<Block, number[]>;
  norm: number;
  decision: string;
  gaps: Record<Block, number>;
  failed_blocks: Block[];
  plan: PlanItem[];
  details: Record<string, unknown>;
  weights: Record<Block, number>;
  gap_trigger: number;
}

export interface Officer {
  id: number;
  full_name: string;
  username: string;
  pinfl: string;
  position: string;
  group: string;
  experience_years: number;
  role: string;
  agency: { id: number; name: string; category: string; region: string; norm_threshold: number };
}

export interface RegistryRow extends Officer {
  before: SessionSummary | null;
  after: SessionSummary | null;
  latest: SessionSummary | null;
}

export interface Passport {
  officer: Officer;
  sessions: SessionSummary[];
  session: SessionFull | null;
  compare: SessionSummary | null;
}

export interface TTestRow {
  indicator: string;
  n: number;
  before_mean: number;
  before_sd: number;
  after_mean: number;
  after_sd: number;
  delta: number;
  delta_pct: number;
  sd_diff: number;
  t: number;
  df: number;
  p: number;
}

export interface Experiment {
  n: number;
  table: TTestRow[];
  levels: { level: string; before: number; after: number; before_pct: number; after_pct: number }[];
  groups: { group: string; label: string; n: number; before: number; after: number }[];
  kpi: {
    n: number;
    i_before: number;
    i_after: number;
    i_delta: number;
    i_delta_pct: number;
    qualified_before_pct: number;
    qualified_after_pct: number;
    avg_minutes: number;
    traditional_minutes: number;
    speedup: number;
    phi_fail_before: number;
    phi_fail_after: number;
    total_sessions: number;
  };
}

export const GROUP_LABELS: Record<string, string> = {
  ministry: "Vazirlik",
  regional: "Viloyat",
  district: "Tuman",
};
