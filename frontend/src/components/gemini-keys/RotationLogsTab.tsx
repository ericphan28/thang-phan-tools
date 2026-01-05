/**
 * Rotation Logs Tab - View key rotation history
 */
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
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
import { RotateCw, ArrowRight } from 'lucide-react';
import { geminiKeysService, type RotationLog } from '../../services/geminiKeysService';
import { Skeleton } from '../ui/skeleton';

export default function RotationLogsTab() {
  const [limit, setLimit] = useState(50);

  const { data: logs, isLoading } = useQuery({
    queryKey: ['gemini-rotation-logs', limit],
    queryFn: () => geminiKeysService.getRotationLogs(limit),
  });

  const getReasonBadge = (reason: string) => {
    const variants: Record<string, { variant: any; color: string }> = {
      quota_exceeded: { variant: 'outline', color: 'border-orange-500 text-orange-600' },
      manual_rotation: { variant: 'default', color: '' },
      key_error: { variant: 'destructive', color: '' },
      revoked: { variant: 'destructive', color: '' },
    };
    const config = variants[reason] || variants.manual_rotation;
    
    return (
      <Badge variant={config.variant} className={config.color}>
        {reason.replace(/_/g, ' ')}
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
      {/* Header */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Rotation Logs</CardTitle>
            <CardDescription>Lịch sử chuyển đổi giữa các API keys</CardDescription>
          </div>
          <div className="w-32">
            <Select
              value={limit.toString()}
              onValueChange={(v) => setLimit(parseInt(v))}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="20">20 records</SelectItem>
                <SelectItem value="50">50 records</SelectItem>
                <SelectItem value="100">100 records</SelectItem>
                <SelectItem value="200">200 records</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
      </Card>

      {/* Logs Table */}
      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Time</TableHead>
                  <TableHead>From Key</TableHead>
                  <TableHead className="w-8"></TableHead>
                  <TableHead>To Key</TableHead>
                  <TableHead>Reason</TableHead>
                  <TableHead>Rotated By</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {logs?.map((log) => (
                  <TableRow key={log.id}>
                    <TableCell className="text-xs">
                      {new Date(log.rotated_at).toLocaleString('vi-VN')}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <RotateCw className="h-4 w-4 text-muted-foreground" />
                        <span className="font-medium">{log.from_key_name || 'N/A'}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <ArrowRight className="h-4 w-4 text-muted-foreground" />
                    </TableCell>
                    <TableCell>
                      <span className="font-medium text-green-600">{log.to_key_name || 'N/A'}</span>
                    </TableCell>
                    <TableCell>
                      {getReasonBadge(log.reason)}
                    </TableCell>
                    <TableCell>
                      <span className="text-xs text-muted-foreground">
                        {log.rotated_by.startsWith('admin:') ? (
                          <>
                            <Badge variant="outline" className="mr-2">Admin</Badge>
                            {log.rotated_by.replace('admin:', '')}
                          </>
                        ) : (
                          <>
                            <Badge variant="secondary" className="mr-2">System</Badge>
                            Auto
                          </>
                        )}
                      </span>
                    </TableCell>
                  </TableRow>
                ))}
                {(!logs || logs.length === 0) && (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center py-8 text-muted-foreground">
                      No rotation logs found
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      {/* Summary */}
      {logs && logs.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Rotation Statistics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <p className="text-muted-foreground">Total Rotations</p>
                <p className="text-xl font-bold">{logs.length}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Quota Exceeded</p>
                <p className="text-xl font-bold text-orange-600">
                  {logs.filter(l => l.reason === 'quota_exceeded').length}
                </p>
              </div>
              <div>
                <p className="text-muted-foreground">Manual Rotations</p>
                <p className="text-xl font-bold text-blue-600">
                  {logs.filter(l => l.reason === 'manual_rotation').length}
                </p>
              </div>
              <div>
                <p className="text-muted-foreground">Key Errors</p>
                <p className="text-xl font-bold text-red-600">
                  {logs.filter(l => l.reason === 'key_error' || l.reason === 'revoked').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
