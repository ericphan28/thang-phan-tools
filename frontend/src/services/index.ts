import api from './api';
import type {
  LoginRequest,
  LoginResponse,
  User,
  UserStats,
  UserListResponse,
  UserCreate,
  UserUpdate,
  Role,
  RoleDetail,
  Permission,
  ActivityLog,
  ActivityLogListResponse,
  ActivityStats,
} from '../types';

export const authService = {
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    const response = await api.post('/auth/login', credentials);
    return response.data;
  },

  logout: async () => {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
    }
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

export const userService = {
  getStats: async (): Promise<UserStats> => {
    const response = await api.get('/users/stats');
    return response.data;
  },

  getUsers: async (params?: {
    search?: string;
    role?: string;
    is_active?: boolean;
    is_superuser?: boolean;
    page?: number;
    page_size?: number;
    sort_by?: string;
    sort_order?: string;
  }): Promise<UserListResponse> => {
    const response = await api.get('/users/', { params });
    return response.data;
  },

  getUserById: async (id: number): Promise<User> => {
    const response = await api.get(`/users/${id}`);
    return response.data;
  },

  createUser: async (data: UserCreate): Promise<User> => {
    const response = await api.post('/users/', data);
    return response.data;
  },

  updateUser: async (id: number, data: UserUpdate): Promise<User> => {
    const response = await api.put(`/users/${id}`, data);
    return response.data;
  },

  deleteUser: async (id: number): Promise<void> => {
    await api.delete(`/users/${id}`);
  },

  assignRoles: async (id: number, roleIds: number[]): Promise<User> => {
    const response = await api.post(`/users/${id}/roles`, { role_ids: roleIds });
    return response.data;
  },

  activateUser: async (id: number): Promise<User> => {
    const response = await api.post(`/users/${id}/activate`);
    return response.data;
  },

  deactivateUser: async (id: number): Promise<User> => {
    const response = await api.post(`/users/${id}/deactivate`);
    return response.data;
  },
};

export const roleService = {
  getRoles: async (): Promise<Role[]> => {
    const response = await api.get('/roles/');
    return response.data;
  },

  getRoleById: async (id: number): Promise<RoleDetail> => {
    const response = await api.get(`/roles/${id}`);
    return response.data;
  },

  getPermissions: async (): Promise<Permission[]> => {
    const response = await api.get('/roles/permissions/all');
    return response.data;
  },

  createRole: async (data: { name: string; description?: string; permission_ids?: number[] }): Promise<RoleDetail> => {
    const response = await api.post('/roles/', data);
    return response.data;
  },

  updateRole: async (id: number, data: { description?: string; permission_ids?: number[] }): Promise<RoleDetail> => {
    const response = await api.put(`/roles/${id}`, data);
    return response.data;
  },

  deleteRole: async (id: number): Promise<void> => {
    await api.delete(`/roles/${id}`);
  },

  getRoleUsers: async (id: number): Promise<User[]> => {
    const response = await api.get(`/roles/${id}/users`);
    return response.data;
  },
};

export const activityLogService = {
  getLogs: async (params?: {
    page?: number;
    page_size?: number;
    user_id?: number;
    action?: string;
    resource_type?: string;
    date_from?: string;
    date_to?: string;
    search?: string;
  }): Promise<ActivityLogListResponse> => {
    const response = await api.get('/logs/', { params });
    return response.data;
  },

  getStats: async (days: number = 7): Promise<ActivityStats> => {
    const response = await api.get('/logs/stats', { params: { days } });
    return response.data;
  },
};
