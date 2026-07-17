import * as LucideIcons from 'lucide-react';
import { PrimaryButton } from './PrimaryButton';
import './EmptyState.css';

interface EmptyStateProps {
  icon?: string;
  title: string;
  description: string;
  buttonText?: string;
  buttonDisabled?: boolean;
  onButtonClick?: () => void;
}

export function EmptyState({
  icon = 'Inbox',
  title,
  description,
  buttonText,
  buttonDisabled = true,
  onButtonClick,
}: EmptyStateProps) {
  const IconComponent = (LucideIcons as unknown as Record<string, React.ComponentType<{ size?: number; className?: string }>>)[icon];

  return (
    <div className="empty-state">
      <div className="empty-state__icon-wrap">
        {IconComponent && <IconComponent size={48} className="empty-state__icon" />}
        <div className="empty-state__icon-ring" />
      </div>
      <h3 className="empty-state__title">{title}</h3>
      <p className="empty-state__description">{description}</p>
      {buttonText && (
        <div className="empty-state__action">
          <PrimaryButton disabled={buttonDisabled} onClick={onButtonClick}>
            {buttonText}
          </PrimaryButton>
        </div>
      )}
    </div>
  );
}
