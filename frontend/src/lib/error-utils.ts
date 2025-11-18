/**
 * Format API error for display in toast
 */
export function formatApiError(error: any): string {
  const errorDetail = error.response?.data?.detail;
  
  if (typeof errorDetail === 'string') {
    return errorDetail;
  }
  
  if (Array.isArray(errorDetail)) {
    return errorDetail
      .map((e: any) => e.msg || e.message || JSON.stringify(e))
      .join(', ');
  }
  
  if (typeof errorDetail === 'object' && errorDetail !== null) {
    // Pydantic validation errors
    if (errorDetail.msg) {
      return errorDetail.msg;
    }
    return JSON.stringify(errorDetail);
  }
  
  return error.message || 'Có lỗi xảy ra';
}
