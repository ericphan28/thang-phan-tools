import { cn } from "../../lib/utils";

function Skeleton({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("animate-pulse rounded-md bg-muted", className)}
      {...props}
    />
  );
}

// Card Skeleton for stats
function StatCardSkeleton() {
  return (
    <div className="rounded-lg border bg-card p-6 space-y-3">
      <div className="flex items-center justify-between">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-10 w-10 rounded-full" />
      </div>
      <Skeleton className="h-8 w-16" />
    </div>
  );
}

// Table Row Skeleton
function TableRowSkeleton() {
  return (
    <div className="grid grid-cols-12 gap-4 px-4 py-3 border rounded-lg">
      <div className="col-span-3 space-y-2">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-3 w-32" />
      </div>
      <div className="col-span-3">
        <Skeleton className="h-4 w-40" />
      </div>
      <div className="col-span-2">
        <Skeleton className="h-6 w-16 rounded-full" />
      </div>
      <div className="col-span-1">
        <Skeleton className="h-6 w-16" />
      </div>
      <div className="col-span-1">
        <Skeleton className="h-6 w-12" />
      </div>
      <div className="col-span-2 flex gap-2 justify-end">
        <Skeleton className="h-8 w-20" />
        <Skeleton className="h-8 w-8" />
        <Skeleton className="h-8 w-8" />
      </div>
    </div>
  );
}

// Role Card Skeleton
function RoleCardSkeleton() {
  return (
    <div className="rounded-lg border bg-card p-6 space-y-3">
      <div className="flex items-center gap-3">
        <Skeleton className="h-10 w-10 rounded-lg" />
        <div className="flex-1 space-y-2">
          <Skeleton className="h-5 w-24" />
          <Skeleton className="h-3 w-32" />
        </div>
      </div>
    </div>
  );
}

// Permission Grid Skeleton
function PermissionGridSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
      {[...Array(6)].map((_, i) => (
        <div key={i} className="p-3 border rounded-lg space-y-2">
          <Skeleton className="h-4 w-32" />
          <Skeleton className="h-3 w-40" />
        </div>
      ))}
    </div>
  );
}

export { 
  Skeleton, 
  StatCardSkeleton, 
  TableRowSkeleton, 
  RoleCardSkeleton,
  PermissionGridSkeleton 
};
