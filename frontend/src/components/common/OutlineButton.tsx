import type { ReactNode, ButtonHTMLAttributes } from 'react';
import './OutlineButton.css';

interface OutlineButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'danger';
}

export function OutlineButton({
  children,
  size = 'md',
  variant = 'default',
  className = '',
  disabled,
  ...props
}: OutlineButtonProps) {
  return (
    <button
      className={`outline-btn outline-btn--${size} outline-btn--${variant} ${className}`}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
}
