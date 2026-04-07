import React from 'react';
import { Shield, AlertTriangle, CheckCircle } from 'lucide-react';

interface ConfidenceBadgeProps {
  score: number;
  showLabel?: boolean;
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
}

export const ConfidenceBadge: React.FC<ConfidenceBadgeProps> = ({
  score,
  showLabel = true,
  size = 'md',
  showIcon = true
}) => {
  const getConfidenceLevel = (score: number) => {
    if (score >= 80) return { level: 'High', color: 'green', icon: CheckCircle };
    if (score >= 60) return { level: 'Medium', color: 'yellow', icon: Shield };
    return { level: 'Low', color: 'red', icon: AlertTriangle };
  };

  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return {
          container: 'px-2 py-0.5 text-xs',
          icon: 'w-3 h-3'
        };
      case 'lg':
        return {
          container: 'px-4 py-2 text-base',
          icon: 'w-5 h-5'
        };
      default:
        return {
          container: 'px-3 py-1 text-sm',
          icon: 'w-4 h-4'
        };
    }
  };

  const getColorClasses = (color: string) => {
    switch (color) {
      case 'green':
        return 'bg-green-100 text-green-700 border-green-300';
      case 'yellow':
        return 'bg-yellow-100 text-yellow-700 border-yellow-300';
      case 'red':
        return 'bg-red-100 text-red-700 border-red-300';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-300';
    }
  };

  const confidence = getConfidenceLevel(score);
  const sizeClasses = getSizeClasses();
  const Icon = confidence.icon;

  return (
    <div
      className={`
        inline-flex items-center gap-1.5 font-semibold rounded-full border
        ${sizeClasses.container}
        ${getColorClasses(confidence.color)}
      `}
      title={`Confidence: ${score}%`}
    >
      {showIcon && <Icon className={sizeClasses.icon} />}
      <span>{score}%</span>
      {showLabel && <span className="font-normal">{confidence.level}</span>}
    </div>
  );
};
