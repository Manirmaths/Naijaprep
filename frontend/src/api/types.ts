export interface User {
  id: number;
  username: string;
  email: string;
  points: number;
  is_admin: boolean;
  is_premium: boolean;
  current_streak: number;
  longest_streak: number;
  streak_freezes: number;
  daily_goal: number;
  has_taken_diagnostic: boolean;
}

export interface Subject {
  name: string;
  question_count: number;
}

export interface Topic {
  name: string;
  count: number;
}

export type Difficulty = 'easy' | 'medium' | 'hard';
export type QuestionSource = 'original' | 'past-question' | 'licensed';
export type QuestionStatus = 'active' | 'draft';

export interface Passage {
  passage_id: string;
  subject: string | null;
  title: string | null;
  passage_text: string;
}

export interface QuestionPublic {
  id: number;
  question_id: string | null;
  subject: string | null;
  topic: string | null;
  subtopic: string | null;
  difficulty: Difficulty;
  question_text: string;
  image_url: string | null;
  option_a: string;
  option_b: string;
  option_c: string;
  option_d: string;
  year: string | null;
  passage: Passage | null;
}

export interface QuizAttempt {
  attempt_id: number;
  mode: string;
  total: number;
  current_index: number;
  time_limit_seconds: number | null;
  per_question_seconds: number | null;
  current_question: QuestionPublic | null;
  finished: boolean;
  score: number;
}

export interface AnswerResult {
  is_correct: boolean;
  correct_option: string;
  explanation: string | null;
  next: QuizAttempt;
}

export interface ResultItem {
  question_id: number;
  question_text: string;
  image_url: string | null;
  selected_option: string;
  correct_option: string;
  is_correct: boolean;
  is_marked: boolean;
  explanation: string | null;
}

export interface QuizResults {
  score: number;
  total: number;
  items: ResultItem[];
}

export interface TopicStat {
  topic: string;
  correct: number;
  total: number;
  percentage: number;
}

export interface ScoreEstimate {
  available: boolean;
  projected_low: number | null;
  projected_high: number | null;
  based_on_answers: number;
  message: string | null;
}

export interface Dashboard {
  points: number;
  current_streak: number;
  longest_streak: number;
  streak_freezes: number;
  daily_goal: number;
  points_today: number;
  goal_met: boolean;
  has_taken_diagnostic: boolean;
  topic_stats: TopicStat[];
  review_count: number;
  exam_years: string[];
  recommended_topics: TopicStat[];
  due_for_review_count: number;
  score_estimate: ScoreEstimate;
}

export interface TutorAskResponse {
  reply: string;
  queries_remaining_today: number;
}

export interface SuggestTagsResponse {
  subject: string | null;
  topic: string | null;
  subtopic: string | null;
  difficulty: Difficulty | null;
  note: string | null;
}

export interface Achievement {
  code: string;
  title: string;
  description: string;
  icon: string;
  earned: boolean;
  earned_at: string | null;
  newly_unlocked: boolean;
}

export interface AchievementsResponse {
  items: Achievement[];
  newly_unlocked: string[];
}

export interface AdminQuestion {
  id: number;
  question_id: string;
  subject: string;
  topic: string;
  subtopic: string | null;
  difficulty: Difficulty;
  exam_type: string | null;
  year: string | null;
  passage_id: string | null;
  question_text: string;
  image_url: string | null;
  option_a: string;
  option_b: string;
  option_c: string;
  option_d: string;
  correct_option: string;
  explanation: string | null;
  tags: string | null;
  source: QuestionSource;
  status: QuestionStatus;
}

export interface AdminStats {
  total_questions: number;
  total_users: number;
  subjects: string[];
}

export interface AdminUser {
  id: number;
  username: string;
  email: string;
  points: number;
  is_admin: boolean;
  current_streak: number;
  longest_streak: number;
  created_at: string;
}

export interface LeaderboardEntry {
  rank: number;
  username: string;
  points: number;
  current_streak: number;
  is_you: boolean;
}

export interface Leaderboard {
  entries: LeaderboardEntry[];
  your_rank: number;
  your_points: number;
}
