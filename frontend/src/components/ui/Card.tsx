import type { HTMLAttributes, ReactNode } from 'react';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  interactive?: boolean;
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

const paddingClasses = {
  none: '',
  sm: 'p-4',
  md: 'p-6',
  lg: 'p-8',
};

export default function Card({ children, interactive, padding = 'md', className = '', ...rest }: CardProps) {
  return (
    <div
      className={`bg-white rounded-2xl border border-ink-100 shadow-[0_1px_2px_rgba(22,23,43,0.04),0_4px_16px_rgba(22,23,43,0.06)] ${
        interactive ? 'transition-all duration-200 hover:shadow-[0_2px_4px_rgba(22,23,43,0.06),0_12px_32px_rgba(22,23,43,0.10)] hover:-translate-y-0.5 cursor-pointer' : ''
      } ${paddingClasses[padding]} ${className}`}
      {...rest}
    >
      {children}
    </div>
  );
}
