import type { ReactNode } from 'react';

export default function EmptyState({
  icon = 'fa-solid fa-inbox',
  title,
  description,
  action,
}: {
  icon?: string;
  title: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center text-center py-16 px-6">
      <div className="w-14 h-14 rounded-2xl bg-ink-100 flex items-center justify-center text-ink-400 text-xl mb-4">
        <i className={icon} />
      </div>
      <h3 className="font-display font-bold text-ink-900 text-lg mb-1">{title}</h3>
      {description && <p className="text-sm text-ink-500 max-w-sm mb-5">{description}</p>}
      {action}
    </div>
  );
}
