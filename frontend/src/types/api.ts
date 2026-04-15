// API Response Types

export interface DailyProblem {
  title: string;
  slug: string;
  url: string;
  difficulty: string;
  description: string;
  fetched_at: string;
  acceptance_rate: number | null;
  topic_tags: string[];
}

export interface Timer {
  expires_at: string;
  hours_remaining: number;
  minutes_remaining: number;
  display_text: string;
}

export interface HomeResponse {
  status: string;
  daily_problem: DailyProblem | null;
}

export interface ProblemResponse {
  status: string;
  daily_problem: DailyProblem | null;
  timer: Timer | null;
}

export interface RecipientResponse {
  status: string;
  message: string;
  email?: string;
}

export interface RefreshResponse {
  status: string;
  message: string;
  sent_count: number;
}

export interface ErrorResponse {
  status: string;
  message: string;
  missing?: string[];
}
