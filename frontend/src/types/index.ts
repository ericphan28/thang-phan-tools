export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
  roles: string[];
}

export interface Role {
  id: number;
  name: string;
  description: string | null;
}

export interface RoleDetail extends Role {
  permissions: Permission[];
}

export interface Permission {
  id: number;
  role_id: number;
  resource: string;
  action: string;
  name: string; // Computed field: resource.action
  description: string; // Computed field: Vietnamese description
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  success: boolean;
  message: string;
  user: User;
  token: {
    access_token: string;
    token_type: string;
    expires_in: number;
  };
}

export interface UserStats {
  total_users: number;
  active_users: number;
  inactive_users: number;
  superusers: number;
}

export interface UserListResponse {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  users: User[];
}

export interface UserCreate {
  username: string;
  email: string;
  password: string;
  full_name?: string;
  is_active?: boolean;
  is_superuser?: boolean;
  role_ids?: number[];
}

export interface UserUpdate {
  email?: string;
  full_name?: string;
  is_active?: boolean;
  is_superuser?: boolean;
  password?: string;
}

export interface ActivityLog {
  id: number;
  user_id: number | null;
  username: string;
  action: string;
  resource_type: string;
  resource_id: number | null;
  details: string | null;
  ip_address: string | null;
  created_at: string;
}

export interface ActivityLogListResponse {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  logs: ActivityLog[];
}

export interface ActivityStats {
  total_activities: number;
  days_analyzed: number;
  by_action: Record<string, number>;
  by_resource: Record<string, number>;
  top_users: Array<{
    user_id: number;
    username: string;
    activity_count: number;
  }>;
}
