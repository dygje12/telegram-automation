import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  MessageSquare, 
  Users, 
  Ban, 
  Play, 
  Pause, 
  Clock,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Loader2
} from 'lucide-react';
import { api } from "../api/client";

export const Dashboard = () => {
  const [stats, setStats] = useState({
    scheduler: null,
    messages: null,
    groups: null,
    blacklist: null,
    logs: null
  });
  const [loading, setLoading] = useState(true);
  const [schedulerLoading, setSchedulerLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadDashboardData();
    
    // Refresh data every 30 seconds
    const interval = setInterval(loadDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      const [schedulerRes, messagesRes, groupsRes, blacklistRes, logsRes] = await Promise.all([
        api.scheduler.getStatus(),
        api.messages.getStats(),
        api.groups.getStats(),
        api.blacklist.getStats(),
        api.scheduler.getLogStats(24)
      ]);

      setStats({
        scheduler: schedulerRes.data,
        messages: messagesRes.data,
        groups: groupsRes.data,
        blacklist: blacklistRes.data,
        logs: logsRes.data
      });
      setError('');
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error('Dashboard data error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSchedulerToggle = async () => {
    try {
      setSchedulerLoading(true);
      
      if (stats.scheduler?.is_running) {
        await api.scheduler.stop();
      } else {
        await api.scheduler.start();
      }
      
      // Refresh scheduler status
      const response = await api.scheduler.getStatus();
      setStats(prev => ({
        ...prev,
        scheduler: response.data
      }));
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to toggle scheduler');
    } finally {
      setSchedulerLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleString();
  };

  const formatInterval = (seconds) => {
    if (!seconds) return 'N/A';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Scheduler Status */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Scheduler</CardTitle>
            {stats.scheduler?.is_running ? (
              <Play className="h-4 w-4 text-green-600" />
            ) : (
              <Pause className="h-4 w-4 text-gray-400" />
            )}
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <Badge 
                variant={stats.scheduler?.is_running ? "default" : "secondary"}
                className={stats.scheduler?.is_running ? "bg-green-100 text-green-800" : ""}
              >
                {stats.scheduler?.is_running ? 'Running' : 'Stopped'}
              </Badge>
              <Button
                size="sm"
                variant={stats.scheduler?.is_running ? "destructive" : "default"}
                onClick={handleSchedulerToggle}
                disabled={schedulerLoading}
              >
                {schedulerLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : stats.scheduler?.is_running ? (
                  'Stop'
                ) : (
                  'Start'
                )}
              </Button>
            </div>
            {stats.scheduler?.next_run && (
              <p className="text-xs text-muted-foreground mt-2">
                Next: {formatDate(stats.scheduler.next_run)}
              </p>
            )}
          </CardContent>
        </Card>

        {/* Messages */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Messages</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.messages?.active || 0}</div>
            <p className="text-xs text-muted-foreground">
              {stats.messages?.total || 0} total ({stats.messages?.inactive || 0} inactive)
            </p>
          </CardContent>
        </Card>

        {/* Groups */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Groups</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.scheduler?.active_groups || 0}</div>
            <p className="text-xs text-muted-foreground">
              {stats.groups?.total || 0} total ({stats.scheduler?.blacklisted_groups || 0} blacklisted)
            </p>
          </CardContent>
        </Card>

        {/* Success Rate */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats.logs?.success_rate ? `${Math.round(stats.logs.success_rate)}%` : '0%'}
            </div>
            <p className="text-xs text-muted-foreground">
              Last 24 hours
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Scheduler Details */}
        <Card>
          <CardHeader>
            <CardTitle>Scheduler Details</CardTitle>
            <CardDescription>Current scheduler status and statistics</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm font-medium">Status</p>
                <p className="text-2xl font-bold">
                  {stats.scheduler?.is_running ? 'Running' : 'Stopped'}
                </p>
              </div>
              <div>
                <p className="text-sm font-medium">Messages Sent</p>
                <p className="text-2xl font-bold">{stats.scheduler?.total_messages_sent || 0}</p>
              </div>
            </div>
            
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm">Last Run:</span>
                <span className="text-sm text-muted-foreground">
                  {formatDate(stats.scheduler?.last_run)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">Next Run:</span>
                <span className="text-sm text-muted-foreground">
                  {formatDate(stats.scheduler?.next_run)}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity (24h)</CardTitle>
            <CardDescription>Message sending statistics</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center">
                <div className="flex items-center justify-center mb-2">
                  <CheckCircle className="w-8 h-8 text-green-500" />
                </div>
                <p className="text-2xl font-bold">{stats.logs?.success || 0}</p>
                <p className="text-xs text-muted-foreground">Successful</p>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center mb-2">
                  <XCircle className="w-8 h-8 text-red-500" />
                </div>
                <p className="text-2xl font-bold">{stats.logs?.failed || 0}</p>
                <p className="text-xs text-muted-foreground">Failed</p>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center mb-2">
                  <Ban className="w-8 h-8 text-yellow-500" />
                </div>
                <p className="text-2xl font-bold">{stats.logs?.blacklisted || 0}</p>
                <p className="text-xs text-muted-foreground">Blacklisted</p>
              </div>
            </div>
            
            <div className="pt-4 border-t">
              <div className="flex justify-between">
                <span className="text-sm">Total Messages:</span>
                <span className="text-sm font-medium">{stats.logs?.total || 0}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Common tasks and shortcuts</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Button variant="outline" className="h-20 flex flex-col gap-2">
              <MessageSquare className="w-6 h-6" />
              <span className="text-sm">Add Message</span>
            </Button>
            <Button variant="outline" className="h-20 flex flex-col gap-2">
              <Users className="w-6 h-6" />
              <span className="text-sm">Add Group</span>
            </Button>
            <Button variant="outline" className="h-20 flex flex-col gap-2">
              <Ban className="w-6 h-6" />
              <span className="text-sm">View Blacklist</span>
            </Button>
            <Button variant="outline" className="h-20 flex flex-col gap-2">
              <Clock className="w-6 h-6" />
              <span className="text-sm">View Logs</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

