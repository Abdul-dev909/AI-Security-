import type { ReactNode, ButtonHTMLAttributes } from 'react';
import './PrimaryButton.css';

interface PrimaryButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  size?: 'sm' | 'md' | 'lg';
}

export function PrimaryButton({
  children,
  size = 'md',
  className = '',
  disabled,
  ...props
}: PrimaryButtonProps) {
  return (
    <button
      className={`primary-btn primary-btn--${size} ${className}`}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
}
