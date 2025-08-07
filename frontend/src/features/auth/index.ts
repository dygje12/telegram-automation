// Auth feature exports
export { default as LoginForm } from '../../components/auth/LoginForm';
export { default as CodeVerification } from '../../components/auth/CodeVerification';
export { default as TwoFactorAuth } from '../../components/auth/TwoFactorAuth';

// Re-export auth hooks
export { default as useAuth } from '../../hooks/useAuth';

// Auth types
export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  loading: boolean;
  error: string | null;
}

export interface User {
  id: string;
  phone: string;
  firstName?: string;
  lastName?: string;
  username?: string;
}

export interface LoginCredentials {
  phone: string;
  code?: string;
  password?: string;
}

export interface AuthResponse {
  token: string;
  user: User;
  message: string;
}

