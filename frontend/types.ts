
export interface PaginatedResult<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export enum UserRole {
  STUDENT = 'STUDENT',
  PARENT = 'PARENT',
  ADMIN = 'ADMIN',
  EDITOR = 'EDITOR',
  TEACHER = 'TEACHER',
  GUEST = 'GUEST'
}

export interface User {
  id: string;
  name: string;
  email?: string;
  phone?: string;
  avatarUrl?: string;
  role: UserRole;
  gradeLevelId?: string;
  level: number;
  xp: number;
  xpToNextLevel: number;
  streak: number;
  smartScore: number; // 0-100
  subscriptionTier: SubscriptionTier;
  lastSyncedAt?: number;
}

export interface GradeLevel {
  id: string;
  name: string;
  slug: string;
  description?: string;
  order: number;
}

export enum SubscriptionTier {
  FREE = 'FREE',
  PREMIUM = 'PREMIUM'
}

export interface Profile {
  id: string;
  displayName: string;
  avatarUrl: string;
  gradeLevelId?: string;
  isActive: boolean;
  hasPin: boolean;
  subscriptionTier: SubscriptionTier;
  weeklyGoalMinutes: number;
}

export enum PaymentProvider {
  KKIAPAY = 'KKIAPAY',
  FEDAPAY = 'FEDAPAY',
  MTN_MOMO = 'MTN_MOMO',
  MOOV_MONEY = 'MOOV_MONEY'
}

export interface Plan {
  id: string;
  name: string;
  price: number; // FCFA
  durationLabel: string; // "mois", "an"
  features: string[];
  isPopular?: boolean;
}

export enum SyncStatus {
  SYNCED = 'SYNCED',
  SYNCING = 'SYNCING',
  PENDING = 'PENDING',
  ERROR = 'ERROR',
  OFFLINE = 'OFFLINE'
}

export type SyncType = 'exercise_attempt' | 'badge_claim' | 'profile_update' | 'analytics' | 'notification_read';

export interface SyncItem {
  id: string; // UUID
  type: SyncType;
  payload: any;
  priority: number; // 1 (High) to 5 (Low)
  timestamp: number; // Created At
  retryCount: number;
  lastAttempt?: number; // Timestamp of last failure
}

// --- Content Pack & Offline Types ---

export interface ContentPack {
  id: string;
  title: string;
  subjectId: string;
  version: string; // Semantic versioning e.g. "1.2.0"
  size: number; // in bytes
  checksum: string; // MD5/SHA for integrity check
  description: string;
  itemsCount: number; // Number of exercises/lessons
  thumbnail?: string;
}

export interface InstalledPack extends ContentPack {
  installedAt: number;
  lastUsedAt: number;
  isUpdateAvailable: boolean;
}

/** Per-skill micro pack metadata from the API */
export interface SkillPack {
  skill_id: string;
  skill_name: string;
  skill_slug: string;
  domain_id: string;
  domain_name: string;
  subject_id: string;
  subject_name: string;
  questions_count: number;
  lessons_count: number;
  estimated_size_bytes: number;
  version: string | null;
}

/** Full per-skill content pack (downloaded JSON) */
export interface SkillPackData {
  skill_id: string;
  skill_name: string;
  skill_slug: string;
  domain_id: string | null;
  domain_name: string | null;
  subject_id: string | null;
  subject_name: string | null;
  micro_skills: any[];
  questions: any[];
  lessons: any[];
  checksum: string;
  generated_at: string;
}

/** Installed skill pack tracked in IndexedDB */
export interface InstalledSkillPack {
  skillId: string;
  skillName: string;
  subjectName: string;
  domainName: string;
  questionsCount: number;
  lessonsCount: number;
  sizeBytes: number;
  checksum: string;
  version: string;
  installedAt: number;
  lastUsedAt: number;
}

export interface StorageStats {
  used: number;
  quota: number;
  percentUsed: number;
}

export interface NavItem {
  label: string;
  path: string;
  icon: string; // Lucide icon name
  allowedRoles: UserRole[]; // RBAC
}

export enum ButtonVariant {
  PRIMARY = 'primary',
  SECONDARY = 'secondary',
  GHOST = 'ghost',
  DANGER = 'danger',
  SUCCESS = 'success'
}

// --- Notification Types ---

export enum NotificationType {
  STREAK_DANGER = 'STREAK_DANGER',
  BADGE_EARNED = 'BADGE_EARNED',
  REPORT_READY = 'REPORT_READY',
  SYSTEM = 'SYSTEM',
  REMINDER = 'REMINDER'
}

export interface AppNotification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  timestamp: string; // ISO string for simplicity in mocks
  read: boolean;
  actionUrl?: string;
}

// --- Skill with progress (shared by Domains, Skills, SkillItem) ---

export interface SkillWithProgress {
  id: string;
  name: string;
  slug: string;
  description?: string;
  domainId: string;
  domainName?: string;
  order: number;
  score: number;
  status: 'locked' | 'todo' | 'started' | 'mastered';
}

// --- Exercise & Content Types ---

export type QuestionType =
  | 'MCQ'
  | 'TRUE_FALSE'
  | 'FILL_BLANK'
  | 'NUMERIC_INPUT'
  | 'SHORT_ANSWER'
  | 'ORDERING'
  | 'MATCHING'
  | 'ERROR_CORRECTION'
  | 'CONTEXTUAL_PROBLEM'
  | 'GUIDED_STEPS'
  | 'JUSTIFICATION'
  | 'TRACING'
  | 'DRAG_DROP'
  | 'INTERACTIVE_DRAW'
  | 'CHART_INPUT'
  | 'AUDIO_COMPREHENSION';

export interface MediaReference {
  id: string;
  type: 'image' | 'svg' | 'animation' | 'video' | 'audio' | 'diagram' | 'interactive_canvas' | 'interactive_chart' | 'interactive_diagram';
  url: string;
  alt_text: string;
  interactive?: boolean;
  dimensions?: { width: number; height: number };
  duration_seconds?: number;
  transcript_available?: boolean;
  trigger?: string;
}

export interface InteractiveConfig {
  type: 'drag_drop' | 'draw' | 'chart_input' | 'audio_quiz' | 'click_zone' | 'slider' | 'match';
  config: any;
}

export interface Question {
  id: string;
  type: QuestionType;
  prompt: string;
  imageUrl?: string;
  options?: string[]; // For MCQ
  choices?: any; // Generic JSONB from backend (matching pairs, steps, etc.)
  correctAnswer: string | number | boolean | string[];
  explanation: string;
  hint?: string;
  hints?: string[]; // Progressive hints (up to 3 levels)
  mediaReferences?: MediaReference[];
  interactiveConfig?: InteractiveConfig;
}

export interface Exercise {
  id: string;
  title: string;
  skillId: string; // e.g., '1' for "Lire et écrire..."
  subjectId: string;
  domainId: string;
  questions: Question[];
  xpReward: number;
}

export interface MicroLesson {
  id: string;
  title: string;
  subjectId: string;
  content: string[]; // Paragraphs
  example: {
    title: string;
    content: string;
    highlight: string;
  };
  duration: number; // minutes
}
