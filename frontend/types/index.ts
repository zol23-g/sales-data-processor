// Re-export all types from individual files
export * from './api';
export * from './common';

// Global type definitions
export type {};

// Environment types
declare global {
  namespace NodeJS {
    interface ProcessEnv {
      NEXT_PUBLIC_API_BASE_URL: string;
      NEXT_PUBLIC_APP_ENVIRONMENT: 'development' | 'staging' | 'production';
      NEXT_PUBLIC_APP_VERSION?: string;
    }
  }
}

// Window extensions for development
declare global {
  interface Window {
    __APP_CONFIG__?: {
      environment: string;
      apiBaseUrl: string;
      version: string;
    };
  }
}