/**
 * Billing History Page
 * View past invoices and payment history
 */
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { subscriptionService } from '../services';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { 
  Download, FileText, CheckCircle, Clock, 
  AlertCircle, ChevronLeft, ChevronRight 
} from 'lucide-react';
import { formatCurrency } from '../lib/utils';
import { Link } from 'react-router-dom';

export default function BillingHistoryPage() {
  const [page, setPage] = useState(1);
  const pageSize = 12;

  // Query billing history
  const { data: billing, isLoading } = useQuery({
    queryKey: ['my-billing', page],
    queryFn: () => subscriptionService.getMyBilling(page, pageSize),
  });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'paid':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded">
            <CheckCircle className="h-3 w-3" />
            Paid
          </span>
        );
      case 'pending':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 bg-yellow-100 text-yellow-800 text-xs font-medium rounded">
            <Clock className="h-3 w-3" />
            Pending
          </span>
        );
      case 'overdue':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 bg-red-100 text-red-800 text-xs font-medium rounded">
            <AlertCircle className="h-3 w-3" />
            Overdue
          </span>
        );
      default:
        return status;
    }
  };

  const formatMonth = (month: string) => {
    const [year, monthNum] = month.split('-');
    const date = new Date(parseInt(year), parseInt(monthNum) - 1);
    return date.toLocaleDateString('vi-VN', { year: 'numeric', month: 'long' });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Billing History</h1>
          <p className="text-muted-foreground mt-1">
            View your past invoices and payment history
          </p>
        </div>
        <Link to="/subscription">
          <Button variant="outline">Back to Subscription</Button>
        </Link>
      </div>

      {isLoading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading billing history...</p>
        </div>
      ) : billing && billing.records.length > 0 ? (
        <>
          {/* Billing Records */}
          <div className="space-y-4">
            {billing.records.map((record) => (
              <Card key={record.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="grid gap-4 md:grid-cols-12 items-center">
                    {/* Month & Period */}
                    <div className="md:col-span-3">
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-primary/10 rounded">
                          <FileText className="h-5 w-5 text-primary" />
                        </div>
                        <div>
                          <div className="font-semibold">{formatMonth(record.billing_month)}</div>
                          <div className="text-xs text-muted-foreground">
                            {new Date(record.period_start).toLocaleDateString('vi-VN')} -{' '}
                            {new Date(record.period_end).toLocaleDateString('vi-VN')}
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Usage Stats */}
                    <div className="md:col-span-4 space-y-1">
                      <div className="text-sm">
                        <span className="text-muted-foreground">Requests:</span>{' '}
                        <span className="font-medium">{record.total_requests.toLocaleString()}</span>
                      </div>
                      <div className="text-sm">
                        <span className="text-muted-foreground">Tokens:</span>{' '}
                        <span className="font-medium">{record.total_tokens.toLocaleString()}</span>
                      </div>
                      <div className="text-xs text-muted-foreground">
                        Gemini: {formatCurrency(record.gemini_cost)} | Claude:{' '}
                        {formatCurrency(record.claude_cost)} | Adobe:{' '}
                        {formatCurrency(record.adobe_cost)}
                      </div>
                    </div>

                    {/* Costs */}
                    <div className="md:col-span-2 text-center">
                      <div className="text-xs text-muted-foreground">Total Amount</div>
                      <div className="text-2xl font-bold">{formatCurrency(record.total_amount)}</div>
                      <div className="text-xs text-muted-foreground mt-1">
                        Usage: {formatCurrency(record.total_cost)}
                        <br />
                        Subscription: {formatCurrency(record.subscription_fee)}
                      </div>
                    </div>

                    {/* Status & Actions */}
                    <div className="md:col-span-3 flex items-center justify-end gap-2">
                      <div>{getStatusBadge(record.status)}</div>
                      {record.invoice_url ? (
                        <a href={record.invoice_url} target="_blank" rel="noopener noreferrer">
                          <Button size="sm" variant="outline">
                            <Download className="h-4 w-4 mr-1" />
                            Invoice
                          </Button>
                        </a>
                      ) : (
                        <Button size="sm" variant="outline" disabled>
                          <Download className="h-4 w-4 mr-1" />
                          Invoice
                        </Button>
                      )}
                    </div>
                  </div>

                  {/* Invoice Number */}
                  {record.invoice_number && (
                    <div className="mt-4 pt-4 border-t text-xs text-muted-foreground">
                      Invoice #: {record.invoice_number}
                      {record.paid_at && (
                        <span className="ml-4">
                          Paid: {new Date(record.paid_at).toLocaleDateString('vi-VN')}
                        </span>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Pagination */}
          {billing.total_pages > 1 && (
            <div className="flex justify-center items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
              >
                <ChevronLeft className="h-4 w-4" />
                Previous
              </Button>
              <span className="text-sm text-muted-foreground">
                Page {page} of {billing.total_pages}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => Math.min(billing.total_pages, p + 1))}
                disabled={page === billing.total_pages}
              >
                Next
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          )}

          {/* Summary Card */}
          <Card>
            <CardHeader>
              <CardTitle>Total Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-4">
                <div>
                  <div className="text-sm text-muted-foreground">Total Bills</div>
                  <div className="text-2xl font-bold">{billing.total}</div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">Total Amount</div>
                  <div className="text-2xl font-bold">
                    {formatCurrency(
                      billing.records.reduce((sum, r) => sum + r.total_amount, 0)
                    )}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">Total Requests</div>
                  <div className="text-2xl font-bold">
                    {billing.records.reduce((sum, r) => sum + r.total_requests, 0).toLocaleString()}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">Paid Bills</div>
                  <div className="text-2xl font-bold">
                    {billing.records.filter((r) => r.status === 'paid').length}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </>
      ) : (
        <Card>
          <CardContent className="py-12 text-center">
            <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">No billing history yet</h3>
            <p className="text-muted-foreground mb-4">
              Your billing history will appear here once you start using the service
            </p>
            <Link to="/subscription">
              <Button>View Subscription</Button>
            </Link>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
