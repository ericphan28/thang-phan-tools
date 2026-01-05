/**
 * Usage Logs Tab - View API usage history
 */
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select';
import { CheckCircle2, XCircle, AlertTriangle, Clock } from 'lucide-react';
import { geminiKeysService, type UsageLog } from '../../services/geminiKeysService';
import { Skeleton } from '../ui/skeleton';

export default function UsageLogsTab() {
  const [limit, setLimit] = useState(100);
  const [filterKeyId, setFilterKeyId] = useState<number | undefined>();

  const { data: logs, isLoading } = useQuery({
    queryKey: ['gemini-usage-logs', limit, filterKeyId],
    queryFn: () => geminiKeysService.getUsageLogs({ limit, key_id: filterKeyId }),
  });

  const { data: keys } = useQuery({
    queryKey: ['gemini-keys-for-filter'],
    queryFn: () => geminiKeysService.getAllKeys(false),
  });

  const getStatusBadge = (status: string) => {
    const variants: Record<string, { variant: any; icon: any; color: string }> = {
      success: { variant: 'default', icon: CheckCircle2, color: 'text-green-600' },
      failed: { variant: 'destructive', icon: XCircle, color: 'text-red-600' },
      quota_exceeded: { variant: 'outline', icon: AlertTriangle, color: 'text-orange-600' },
      rate_limited: { variant: 'secondary', icon: Clock, color: 'text-yellow-600' },
      key_error: { variant: 'destructive', icon: XCircle, color: 'text-red-600' },
    };
    const config = variants[status] || variants.failed;
    const Icon = config.icon;
    
    return (
      <Badge variant={config.variant} className="flex items-center gap-1 w-fit">
        <Icon className="h-3 w-3" />
        {status.replace(/_/g, ' ')}
      </Badge>
    );
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-32" />
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {[...Array(5)].map((_, i) => <Skeleton key={i} className="h-12 w-full" />)}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Usage Logs</CardTitle>
          <CardDescription>Chi tiết từng request gọi Gemini API</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label>Filter by Key</Label>
              <Select
                value={filterKeyId?.toString() || 'all'}
                onValueChange={(v) => setFilterKeyId(v === 'all' ? undefined : parseInt(v))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="All keys" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All keys</SelectItem>
                  {keys?.map((key) => (
                    <SelectItem key={key.id} value={key.id.toString()}>
                      {key.key_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Limit</Label>
              <Select
                value={limit.toString()}
                onValueChange={(v) => setLimit(parseInt(v))}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="50">50 records</SelectItem>
                  <SelectItem value="100">100 records</SelectItem>
                  <SelectItem value="200">200 records</SelectItem>
                  <SelectItem value="500">500 records</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Logs Table */}
      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Time</TableHead>
                  <TableHead>Key</TableHead>
                  <TableHead>User</TableHead>
                  <TableHead>Model</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead className="text-right">Tokens</TableHead>
                  <TableHead className="text-right">Cost</TableHead>
                  <TableHead className="text-right">Time (ms)</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {logs?.map((log) => (
                  <TableRow key={log.id}>
                    <TableCell className="text-xs">
                      {new Date(log.created_at).toLocaleString('vi-VN')}
                    </TableCell>
                    <TableCell>
                      <span className="text-xs font-medium">{log.key_name || 'N/A'}</span>
                    </TableCell>
                    <TableCell>
                      <span className="text-xs">{log.username || 'System'}</span>
                    </TableCell>
                    <TableCell>
                      <code className="text-xs bg-muted px-1.5 py-0.5 rounded">
                        {log.model}
                      </code>
                    </TableCell>
                    <TableCell>
                      {log.request_type && (
                        <Badge variant="outline" className="text-xs">
                          {log.request_type}
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell className="text-right font-mono text-xs">
                      {log.total_tokens.toLocaleString()}
                    </TableCell>
                    <TableCell className="text-right font-mono text-xs text-green-600">
                      ${log.cost_usd.toFixed(4)}
                    </TableCell>
                    <TableCell className="text-right font-mono text-xs">
                      {log.response_time_ms?.toLocaleString() || 'N/A'}
                    </TableCell>
                    <TableCell>{getStatusBadge(log.status)}</TableCell>
                  </TableRow>
                ))}
                {(!logs || logs.length === 0) && (
                  <TableRow>
                    <TableCell colSpan={9} className="text-center py-8 text-muted-foreground">
                      No usage logs found
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      {/* Summary Stats */}
      {logs && logs.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <p className="text-muted-foreground">Total Requests</p>
                <p className="text-xl font-bold">{logs.length}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Total Tokens</p>
                <p className="text-xl font-bold">
                  {logs.reduce((sum, log) => sum + log.total_tokens, 0).toLocaleString()}
                </p>
              </div>
              <div>
                <p className="text-muted-foreground">Total Cost</p>
                <p className="text-xl font-bold text-green-600">
                  ${logs.reduce((sum, log) => sum + log.cost_usd, 0).toFixed(2)}
                </p>
              </div>
              <div>
                <p className="text-muted-foreground">Success Rate</p>
                <p className="text-xl font-bold">
                  {((logs.filter(l => l.status === 'success').length / logs.length) * 100).toFixed(1)}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
