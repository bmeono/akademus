import { clsx } from 'clsx';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
  padding?: 'none' | 'sm' | 'md' | 'lg';
  onClick?: () => void;
}

export function Card({ children, className, hover = false, padding = 'md', onClick }: CardProps) {
  const paddingStyles = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };
  
  const Component = onClick ? 'button' : 'div';
  
  return (
    <Component
      onClick={onClick}
      className={clsx(
        'bg-white rounded-2xl shadow-sm border border-slate-100 text-left',
        paddingStyles[padding],
        hover && 'transition-all duration-300 hover:shadow-lg hover:border-slate-200 hover:-translate-y-1',
        onClick && 'cursor-pointer transition-all duration-300 hover:shadow-lg hover:border-slate-200 hover:-translate-y-1',
        className
      )}
    >
      {children}
    </Component>
  );
}

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export function Input({ label, error, className, ...props }: InputProps) {
  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-slate-700 mb-1.5">
          {label}
        </label>
      )}
      <input
        className={clsx(
          'w-full px-4 py-3 rounded-xl border-2 bg-white text-slate-900 placeholder-slate-400',
          'focus:outline-none focus:ring-2 transition-all duration-200',
          error
            ? 'border-error-500 focus:border-error-500 focus:ring-error-500/20'
            : 'border-slate-200 focus:border-primary-500 focus:ring-primary-500/20',
          className
        )}
        {...props}
      />
      {error && <p className="mt-1 text-sm text-error-500">{error}</p>}
    </div>
  );
}

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'primary' | 'success' | 'warning' | 'error';
}

export function Badge({ children, variant = 'primary' }: BadgeProps) {
  const variants = {
    primary: 'bg-primary-100 text-primary-800',
    success: 'bg-success-100 text-success-800',
    warning: 'bg-warning-100 text-warning-800',
    error: 'bg-error-100 text-error-800',
  };
  
  return (
    <span className={clsx('inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium', variants[variant])}>
      {children}
    </span>
  );
}