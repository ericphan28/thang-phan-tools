import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import api from '../services/api';
import toast from 'react-hot-toast';
import { RefreshCw, Clock, GitCommit, Rocket, CheckCircle, XCircle, Loader2 } from 'lucide-react';

interface DeploymentPhaseTimings {
  git_push?: number;
  build?: number;
  pull?: number;
  restart?: number;
  verify?: number;
}

interface Deployment {
  id: number;
  version: string;
  status: string;
  git_commit: string | null;
  deploy_type: string;
  phase_timings: DeploymentPhaseTimings;
  total_time: number | null;
  started_at: string;
  completed_at: string | null;
  error_message: string | null;
}

interface DeploymentListResponse {
  deployments: Deployment[];
  total: number;
}

const STATUS_COLORS: Record<string, string> = {
  pending: 'bg-gray-500',
  git_push: 'bg-blue-500',
  building: 'bg-yellow-500',
  pulling: 'bg-purple-500',
  restarting: 'bg-indigo-500',
  verifying: 'bg-cyan-500',
  success: 'bg-green-500',
  failed: 'bg-red-500',
};

const STATUS_ICONS: Record<string, any> = {
  pending: Clock,
  git_push: GitCommit,
  building: Loader2,
  pulling: Loader2,
  restarting: RefreshCw,
  verifying: Loader2,
  success: CheckCircle,
  failed: XCircle,
};

function DeploymentMonitor() {
  const [deployments, setDeployments] = useState<Deployment[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchDeployments = async (showToast = false) => {
    try {
      if (showToast) setRefreshing(true);
      
      const response = await api.get<DeploymentListResponse>('/deployment/list?limit=20');
      setDeployments(response.data.deployments);
      
      if (showToast) {
        toast.success('Deployments refreshed!');
      }
    } catch (error) {
      console.error('Failed to fetch deployments:', error);
      toast.error('Failed to load deployments');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDeployments();
    
    // Auto-refresh every 15 seconds
    const interval = setInterval(() => {
      fetchDeployments();
    }, 15000);
    
    return () => clearInterval(interval);
  }, []);

  const formatDuration = (seconds: number | undefined) => {
    if (!seconds) return '-';
    if (seconds < 60) return `${seconds.toFixed(1)}s`;
    return `${(seconds / 60).toFixed(1)}m`;
  };

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getStatusIcon = (status: string) => {
    const Icon = STATUS_ICONS[status] || Clock;
    return <Icon className={`h-4 w-4 ${status.includes('ing') ? 'animate-spin' : ''}`} />;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  const latestDeployment = deployments[0];

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Rocket className="h-8 w-8 text-primary" />
            Deployment Monitor
          </h1>
          <p className="text-muted-foreground mt-1">
            Track deployment history and timing metrics
          </p>
        </div>
        <Button
          onClick={() => fetchDeployments(true)}
          disabled={refreshing}
          variant="outline"
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Latest Deployment Card */}
      {latestDeployment && (
        <Card className="border-2 border-primary/20">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-xl">Latest Deployment</CardTitle>
              <Badge className={STATUS_COLORS[latestDeployment.status]}>
                {getStatusIcon(latestDeployment.status)}
                <span className="ml-1.5">{latestDeployment.status.toUpperCase()}</span>
              </Badge>
            </div>
            <CardDescription>
              Version {latestDeployment.version} · {latestDeployment.deploy_type} deploy
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Started</p>
                <p className="font-medium">{formatDateTime(latestDeployment.started_at)}</p>
              </div>
              {latestDeployment.completed_at && (
                <div>
                  <p className="text-sm text-muted-foreground">Completed</p>
                  <p className="font-medium">{formatDateTime(latestDeployment.completed_at)}</p>
                </div>
              )}
              {latestDeployment.total_time && (
                <div>
                  <p className="text-sm text-muted-foreground">Total Time</p>
                  <p className="font-medium text-lg">{formatDuration(latestDeployment.total_time)}</p>
                </div>
              )}
              {latestDeployment.git_commit && (
                <div>
                  <p className="text-sm text-muted-foreground">Commit</p>
                  <p className="font-mono text-xs">{latestDeployment.git_commit.substring(0, 8)}</p>
                </div>
              )}
            </div>

            {/* Phase Timings */}
            {Object.keys(latestDeployment.phase_timings).length > 0 && (
              <div className="mt-4 pt-4 border-t">
                <p className="text-sm font-medium mb-2">Phase Timings:</p>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                  {latestDeployment.phase_timings.git_push && (
                    <div className="text-center p-2 bg-blue-50 dark:bg-blue-950 rounded">
                      <p className="text-xs text-muted-foreground">Git Push</p>
                      <p className="font-bold">{formatDuration(latestDeployment.phase_timings.git_push)}</p>
                    </div>
                  )}
                  {latestDeployment.phase_timings.build && (
                    <div className="text-center p-2 bg-yellow-50 dark:bg-yellow-950 rounded">
                      <p className="text-xs text-muted-foreground">Build</p>
                      <p className="font-bold">{formatDuration(latestDeployment.phase_timings.build)}</p>
                    </div>
                  )}
                  {latestDeployment.phase_timings.pull && (
                    <div className="text-center p-2 bg-purple-50 dark:bg-purple-950 rounded">
                      <p className="text-xs text-muted-foreground">Pull</p>
                      <p className="font-bold">{formatDuration(latestDeployment.phase_timings.pull)}</p>
                    </div>
                  )}
                  {latestDeployment.phase_timings.restart && (
                    <div className="text-center p-2 bg-indigo-50 dark:bg-indigo-950 rounded">
                      <p className="text-xs text-muted-foreground">Restart</p>
                      <p className="font-bold">{formatDuration(latestDeployment.phase_timings.restart)}</p>
                    </div>
                  )}
                  {latestDeployment.phase_timings.verify && (
                    <div className="text-center p-2 bg-cyan-50 dark:bg-cyan-950 rounded">
                      <p className="text-xs text-muted-foreground">Verify</p>
                      <p className="font-bold">{formatDuration(latestDeployment.phase_timings.verify)}</p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {latestDeployment.error_message && (
              <div className="mt-4 p-3 bg-red-50 dark:bg-red-950 rounded border border-red-200 dark:border-red-800">
                <p className="text-sm text-red-600 dark:text-red-400">
                  <strong>Error:</strong> {latestDeployment.error_message}
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Deployment History Table */}
      <Card>
        <CardHeader>
          <CardTitle>Deployment History</CardTitle>
          <CardDescription>Last 20 deployments</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="border-b">
                <tr className="text-left">
                  <th className="pb-3 font-medium text-sm">Version</th>
                  <th className="pb-3 font-medium text-sm">Status</th>
                  <th className="pb-3 font-medium text-sm">Type</th>
                  <th className="pb-3 font-medium text-sm">Started</th>
                  <th className="pb-3 font-medium text-sm">Duration</th>
                  <th className="pb-3 font-medium text-sm">Commit</th>
                </tr>
              </thead>
              <tbody>
                {deployments.map((deployment) => (
                  <tr key={deployment.id} className="border-b last:border-0 hover:bg-muted/50">
                    <td className="py-3 font-medium">{deployment.version}</td>
                    <td className="py-3">
                      <Badge className={STATUS_COLORS[deployment.status]} variant="secondary">
                        {getStatusIcon(deployment.status)}
                        <span className="ml-1.5 text-xs">{deployment.status}</span>
                      </Badge>
                    </td>
                    <td className="py-3">
                      <span className="text-sm text-muted-foreground">{deployment.deploy_type}</span>
                    </td>
                    <td className="py-3 text-sm">{formatDateTime(deployment.started_at)}</td>
                    <td className="py-3 font-mono text-sm">
                      {deployment.total_time ? formatDuration(deployment.total_time) : '-'}
                    </td>
                    <td className="py-3 font-mono text-xs text-muted-foreground">
                      {deployment.git_commit ? deployment.git_commit.substring(0, 8) : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {deployments.length === 0 && (
            <div className="text-center py-12 text-muted-foreground">
              <Rocket className="h-12 w-12 mx-auto mb-3 opacity-20" />
              <p>No deployments yet</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export default DeploymentMonitor;
