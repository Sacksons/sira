// User types
export interface User {
  id: number
  username: string
  email: string
  full_name?: string
  role: 'operator' | 'security_lead' | 'supervisor' | 'admin'
  is_active: boolean
  is_verified: boolean
  created_at: string
  last_login?: string
}

// Auth types
export interface LoginCredentials {
  username: string
  password: string
}

export interface AuthToken {
  access_token: string
  token_type: string
}

// Movement types
export interface Movement {
  id: number
  cargo: string
  route: string
  assets?: string
  stakeholders?: string
  laycan_start: string
  laycan_end: string
  status: 'active' | 'completed' | 'cancelled' | 'delayed'
  current_location?: string
  current_lat?: number
  current_lng?: number
  risk_score: number
  created_at: string
  updated_at?: string
}

// Event types
export interface Event {
  id: number
  movement_id: number
  timestamp: string
  location?: string
  latitude?: number
  longitude?: number
  actor?: string
  event_type: 'planned' | 'actual' | 'security' | 'operational'
  severity: 'info' | 'warning' | 'critical'
  description?: string
  created_at: string
}

// Alert types
export type AlertSeverity = 'Critical' | 'High' | 'Medium' | 'Low'
export type AlertStatus = 'open' | 'acknowledged' | 'assigned' | 'investigating' | 'closed'

export interface Alert {
  id: number
  severity: AlertSeverity
  confidence: number
  sla_timer?: number
  sla_breached: boolean
  domain?: string
  site_zone?: string
  movement_id?: number
  event_id?: number
  status: AlertStatus
  case_id?: number
  description?: string
  rule_id?: string
  rule_name?: string
  assigned_to?: number
  acknowledged_at?: string
  resolved_at?: string
  created_at: string
  updated_at?: string
}

// Case types
export type CasePriority = 'low' | 'medium' | 'high' | 'critical'
export type CaseStatus = 'open' | 'investigating' | 'pending' | 'closed'

export interface Case {
  id: number
  case_number?: string
  title: string
  overview?: string
  status: CaseStatus
  priority: CasePriority
  category?: string
  costs: number
  assigned_to?: number
  created_by?: number
  created_at: string
  updated_at?: string
  closed_at?: string
}

// Evidence types
export interface Evidence {
  id: number
  case_id: number
  evidence_type: string
  file_ref: string
  original_filename?: string
  file_size?: number
  mime_type?: string
  verification_status: 'pending' | 'verified' | 'rejected'
  file_hash?: string
  uploaded_by?: number
  created_at: string
}

// Playbook types
export interface Playbook {
  id: number
  incident_type: string
  domain?: string
  title: string
  description?: string
  steps: string
  estimated_duration?: number
  is_active: boolean
  version: number
  created_at: string
}

// Notification types
export interface Notification {
  id: number
  user_id: number
  notification_type: string
  channel: string
  title: string
  message: string
  priority: string
  is_read: boolean
  read_at?: string
  created_at: string
}

// Dashboard stats
export interface DashboardStats {
  alerts: {
    total: number
    open: number
    critical: number
    today: number
    this_week: number
  }
  cases: {
    total: number
    open: number
    today: number
  }
  sla: {
    breached: number
    at_risk: number
  }
  recent_alerts: Array<{
    id: number
    severity: AlertSeverity
    description?: string
    status: AlertStatus
    created_at: string
  }>
  generated_at: string
}

// API Response types
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

export interface ApiError {
  detail: string
}
