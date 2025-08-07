// Groups feature exports
export interface Group {
  id: string;
  title: string;
  username?: string;
  type: 'channel' | 'group' | 'supergroup';
  memberCount: number;
  isActive: boolean;
  lastMessageAt?: string;
  createdAt: string;
  updatedAt: string;
}

export interface GroupStats {
  total: number;
  active: number;
  inactive: number;
  channels: number;
  groups: number;
  supergroups: number;
}

export interface AddGroupRequest {
  username?: string;
  inviteLink?: string;
  groupId?: string;
}

export interface GroupValidationResult {
  isValid: boolean;
  canSendMessages: boolean;
  memberCount: number;
  error?: string;
}

// Group-related hooks and components would be exported here
// export { default as GroupList } from './components/GroupList';
// export { default as GroupForm } from './components/GroupForm';
// export { default as useGroups } from './hooks/useGroups';

