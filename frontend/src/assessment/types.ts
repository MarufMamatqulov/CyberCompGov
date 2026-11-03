import type { Block } from "../types";

export interface TestItem { code: string; block: Block; sub: string; question: string; options: string[] }

export interface ClassifyLab {
  code: string; block: Block; title: string; type: "classify"; intro: string;
  levels: string[]; storage: string[]; assets: { id: string; name: string }[];
  legal_question: string; legal_options: string[];
}
export interface TerminalLab {
  code: string; block: Block; title: string; type: "terminal"; intro: string; host: string; ip: string; hints: string[];
}
export interface EmailLab {
  code: string; block: Block; title: string; type: "email"; intro: string; headers: string; body: string;
  attachment: { name: string; size: string; sha256: string }; sandbox_report: string[];
  questions: { id: string; text: string; options: string[] }[]; actions: { id: string; text: string }[];
}
export type Lab = ClassifyLab | TerminalLab | EmailLab;

export interface CaseStage { id: string; text: string; options: { id: string; text: string; next: string | null }[] }
export interface CaseItem { code: string; block: Block; title: string; start: string; time_limit: number; stages: CaseStage[] }

export interface Content { tests: TestItem[]; labs: Lab[]; cases: CaseItem[] }

export interface ClassifySubmission { levels: Record<string, number>; storage: Record<string, number>; legal?: number }
export interface TerminalSubmission { history: string[]; transcript: { cmd: string; out: string }[] }
export interface EmailSubmission { answers: Record<string, number>; sandbox_run: boolean; actions: string[] }
export type LabSubmission = Partial<ClassifySubmission & TerminalSubmission & EmailSubmission>;

export interface CaseStep { stage: string; option: string }
export interface CaseProgress { path: CaseStep[]; current: string | null; remaining: number; finished: boolean }
