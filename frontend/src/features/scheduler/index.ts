// Scheduler feature exports
export interface ScheduledJob {
  id: string;
  name: string;
  templateId: string;
  groupIds: string[];
  variables: Record<string, string>;
  cronExpression: string;
  nextRun: string;
  lastRun?: string;
  status: 'active' | 'paused' | 'completed' | 'failed';
  createdAt: string;
  updatedAt: string;
}

export interface JobExecution {
  id: string;
  jobId: string;
  status: 'running' | 'completed' | 'failed';
  startedAt: string;
  completedAt?: string;
  messagesSent: number;
  messagesFailed: number;
  error?: string;
}

export interface CreateJobRequest {
  name: string;
  templateId: string;
  groupIds: string[];
  variables: Record<string, string>;
  cronExpression: string;
  startDate?: string;
  endDate?: string;
}

export interface SchedulerStats {
  totalJobs: number;
  activeJobs: number;
  pausedJobs: number;
  completedJobs: number;
  failedJobs: number;
  nextExecution?: string;
}

// Scheduler-related hooks and components would be exported here
// export { default as JobList } from './components/JobList';
// export { default as JobForm } from './components/JobForm';
// export { default as useScheduler } from './hooks/useScheduler';

