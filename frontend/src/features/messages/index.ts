// Messages feature exports
export interface Message {
  id: string;
  content: string;
  template: string;
  variables: Record<string, string>;
  createdAt: string;
  updatedAt: string;
}

export interface MessageTemplate {
  id: string;
  name: string;
  content: string;
  variables: string[];
  description?: string;
  createdAt: string;
  updatedAt: string;
}

export interface SendMessageRequest {
  templateId: string;
  variables: Record<string, string>;
  groupIds: string[];
  scheduledAt?: string;
}

export interface MessageStats {
  total: number;
  sent: number;
  failed: number;
  pending: number;
}

// Message-related hooks and components would be exported here
// export { default as MessageList } from './components/MessageList';
// export { default as MessageForm } from './components/MessageForm';
// export { default as useMessages } from './hooks/useMessages';

