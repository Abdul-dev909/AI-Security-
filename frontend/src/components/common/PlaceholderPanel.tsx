import './PlaceholderPanel.css';

interface PlaceholderPanelProps {
  title?: string;
  subtitle?: string;
  height?: string;
  className?: string;
}

export function PlaceholderPanel({
  title = 'Visualization',
  subtitle = 'Data will appear here once available',
  height = '320px',
  className = '',
}: PlaceholderPanelProps) {
  return (
    <div className={`placeholder-panel ${className}`} style={{ minHeight: height }}>
      <div className="placeholder-panel__grid">
        {Array.from({ length: 12 }).map((_, i) => (
          <div
            key={i}
            className="placeholder-panel__bar"
            style={{
              height: `${20 + Math.random() * 60}%`,
              animationDelay: `${i * 120}ms`,
            }}
          />
        ))}
      </div>
      <div className="placeholder-panel__overlay">
        <span className="placeholder-panel__title">{title}</span>
        <span className="placeholder-panel__subtitle">{subtitle}</span>
      </div>
      <div className="placeholder-panel__scan-line" />
    </div>
  );
}
