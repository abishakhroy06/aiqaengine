import { cn } from '../../lib/utils';
import { SessionStatus } from '../../types/session';

interface Props {
  status: SessionStatus;
}

const statusConfig: Record<SessionStatus, { label: string; className: string }> = {
  pending: { label: 'Pending', className: 'bg-yellow-100 text-yellow-700 border-yellow-200' },
  generating: { label: 'Generating...', className: 'bg-blue-100 text-blue-700 border-blue-200 animate-pulse' },
  complete: { label: 'Complete', className: 'bg-green-100 text-green-700 border-green-200' },
  failed: { label: 'Failed', className: 'bg-red-100 text-red-700 border-red-200' },
};

export function StatusBadge({ status }: Props) {
  const { label, className } = statusConfig[status];
  return (
    <span className={cn('px-2 py-1 rounded-full text-xs font-medium border', className)}>
      {label}
    </span>
  );
}
