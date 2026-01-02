type ImportMetaEnv = { env?: { VITE_API_BASE_URL?: string; DEV?: boolean } };

const env = (import.meta as unknown as ImportMetaEnv).env ?? {};
const fallbackBase = env.DEV ? "" : "https://clintwin.giize.com";
const base = (env.VITE_API_BASE_URL?.trim() || fallbackBase).replace(/\/$/, "");

function makeUrl(path: string) {
  return base ? `${base}${path}` : path;
}

async function jsonFetch<T>(input: RequestInfo, init?: RequestInit): Promise<T> {
  const res = await fetch(input, init);
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`Request failed: ${res.status} ${res.statusText}${text ? ` - ${text}` : ""}`);
  }
  return res.json() as Promise<T>;
}

export type StartSessionResponse = {
  session_id: string;
  question: {
    question_id: string;
    question_text: string;
    options: string[];
    field_target?: string;
  };
  remaining_candidates: number;
  confidence: number;
  questions_asked: number;
};

export type AkinatorQuestionResponse = {
  type: "question";
  question: {
    question_id: string;
    question_text: string;
    options: string[];
    field_target?: string;
  };
  remaining_candidates: number;
  confidence: number;
  questions_asked: number;
};

export type AkinatorResultResponse = {
  type: "result";
  success: boolean;
  top_match?: {
    medicine: {
      id: string;
      name: string;
      generic_name?: string;
      dosage_form?: string;
      main_use?: string;
      warnings?: string[];
    };
    confidence: number;
  } | null;
  alternatives: Array<{
    medicine: { id: string; name: string };
    confidence: number;
  }>;
  confidence: number;
  questions_asked: number;
  answers_given: Array<{ question_id: string; answer: string }>;
};

export async function startAkinator(): Promise<StartSessionResponse> {
  return jsonFetch<StartSessionResponse>(makeUrl("/api/akinator/start"), {
    method: "POST",
  });
}

export async function submitAkinatorAnswer(
  sessionId: string,
  answer: string
): Promise<AkinatorQuestionResponse | AkinatorResultResponse> {
  return jsonFetch<AkinatorQuestionResponse | AkinatorResultResponse>(makeUrl("/api/akinator/answer"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, answer }),
  });
}

export type InteractionCheckByNamesResponse = {
  success: boolean;
  medicines_checked?: string[];
  interactions_found?: Array<{
    id?: string;
    drugs_involved: string[];
    severity: string;
    description?: string;
    recommendation?: string;
  }>;
  warnings?: Array<{
    severity: string;
    title: string;
    drugs_involved: string[];
    message: string;
    recommendation: string;
  }>;
  has_contraindicated?: boolean;
  has_major?: boolean;
  risk_level?: string;
  summary?: string;
  safe_alternatives?: Array<Record<string, unknown>>;
  message?: string;
};

export async function checkInteractionsByNames(names: string[]): Promise<InteractionCheckByNamesResponse> {
  const params = new URLSearchParams();
  for (const n of names) params.append("medicine_names", n);
  return jsonFetch<InteractionCheckByNamesResponse>(makeUrl(`/api/interactions/check-by-names?${params.toString()}`), {
    method: "POST",
  });
}

export async function getSeverityLevels(): Promise<unknown> {
  return jsonFetch<unknown>(makeUrl("/api/interactions/severity-levels"));
}

export type MedicineListItem = {
  id: string;
  name: string;
  generic_name?: string | null;
  category?: string | null;
  requires_prescription: boolean;
};

export async function getMedicines(): Promise<MedicineListItem[]> {
  return jsonFetch<MedicineListItem[]>(makeUrl("/api/interactions/medicines"));
}

export async function searchMedicines(q: string, limit = 10): Promise<{ query: string; results: MedicineListItem[]; count: number }> {
  const params = new URLSearchParams({ q, limit: String(limit) });
  return jsonFetch<{ query: string; results: MedicineListItem[]; count: number }>(makeUrl(`/api/interactions/medicines/search?${params.toString()}`));
}
