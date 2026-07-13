import { type InputHTMLAttributes, type TextareaHTMLAttributes, type SelectHTMLAttributes, forwardRef, type ReactNode, useState } from 'react';

interface FieldWrapProps {
  label?: string;
  hint?: string;
  error?: string;
  children: ReactNode;
}

export function FieldWrap({ label, hint, error, children }: FieldWrapProps) {
  return (
    <label className="block">
      {label && <span className="block text-sm font-semibold text-ink-800 mb-1.5">{label}</span>}
      {children}
      {error ? (
        <span className="block text-xs text-danger-500 mt-1">{error}</span>
      ) : hint ? (
        <span className="block text-xs text-ink-400 mt-1">{hint}</span>
      ) : null}
    </label>
  );
}

export const baseFieldClasses =
  'w-full rounded-xl border border-ink-200 bg-white px-3.5 py-2.5 text-sm text-ink-900 placeholder:text-ink-400 outline-none transition-colors focus:border-brand-400 focus:ring-4 focus:ring-brand-100 disabled:bg-ink-50 disabled:text-ink-400';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  hint?: string;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(function Input(
  { label, hint, error, className = '', ...rest },
  ref
) {
  return (
    <FieldWrap label={label} hint={hint} error={error}>
      <input ref={ref} className={`${baseFieldClasses} ${error ? 'border-danger-400' : ''} ${className}`} {...rest} />
    </FieldWrap>
  );
});

interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  hint?: string;
  error?: string;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(function Textarea(
  { label, hint, error, className = '', ...rest },
  ref
) {
  return (
    <FieldWrap label={label} hint={hint} error={error}>
      <textarea ref={ref} className={`${baseFieldClasses} ${error ? 'border-danger-400' : ''} ${className}`} {...rest} />
    </FieldWrap>
  );
});

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  hint?: string;
  error?: string;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(function Select(
  { label, hint, error, className = '', children, ...rest },
  ref
) {
  return (
    <FieldWrap label={label} hint={hint} error={error}>
      <select ref={ref} className={`${baseFieldClasses} ${error ? 'border-danger-400' : ''} ${className}`} {...rest}>
        {children}
      </select>
    </FieldWrap>
  );
});

interface PasswordInputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string;
  hint?: string;
  error?: string;
}

export const PasswordInput = forwardRef<HTMLInputElement, PasswordInputProps>(function PasswordInput(
  { label, hint, error, className = '', ...rest },
  ref
) {
  const [visible, setVisible] = useState(false);
  return (
    <FieldWrap label={label} hint={hint} error={error}>
      <div className="relative">
        <input
          ref={ref}
          type={visible ? 'text' : 'password'}
          className={`${baseFieldClasses} pr-10 ${error ? 'border-danger-400' : ''} ${className}`}
          {...rest}
        />
        <button
          type="button"
          tabIndex={-1}
          onClick={() => setVisible((v) => !v)}
          aria-label={visible ? 'Hide password' : 'Show password'}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-ink-400 hover:text-ink-600 transition-colors"
        >
          <i className={visible ? 'fa-solid fa-eye-slash' : 'fa-solid fa-eye'} />
        </button>
      </div>
    </FieldWrap>
  );
});
