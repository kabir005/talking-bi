import React from 'react';
import { AlertTriangle, TrendingUp, TrendingDown, Info } from 'lucide-react';

export interface Anomaly {
  value: number;
  expected_range: [number, number];
  severity: 'low' | 'medium' | 'high';
  deviation: number;
  timestamp?: string;
}

interface AnomalyBadgeProps {
  anomaly: Anomaly;
  showDetails?: boolean;
  size?: 'sm' | 'md' | 'lg';
  position?: 'top' | 'bottom' | 'left' | 'right';
}

export const AnomalyBadge: React.FC<AnomalyBadgeProps> = ({
  anomaly,
  showDetails = false,
  size = 'md',
  position = 'top'
}) => {
  const getSeverityConfig = (severity: string) => {
    switch (severity) {
      case 'high':
        return {
          color: 'bg-red-100 text-red-700 border-red-300',
          icon: <AlertTriangle className="w-full h-full" />,
          label: 'High'
        };
      case 'medium':
        return {
          color: 'bg-yellow-100 text-yellow-700 border-yellow-300',
          icon: <AlertTriangle className="w-full h-full" />,
          label: 'Medium'
        };
      case 'low':
        return {
          color: 'bg-blue-100 text-blue-700 border-blue-300',
          icon: <Info className="w-full h-full" />,
          label: 'Low'
        };
      default:
        return {
          color: 'bg-gray-100 text-gray-700 border-gray-300',
          icon: <Info className="w-full h-full" />,
          label: 'Unknown'
        };
    }
  };

  const getSizeClasses = () => {
    switch (size) {
      case 'sm': return 'w-5 h-5 p-1';
      case 'lg': return 'w-10 h-10 p-2';
      default: return 'w-7 h-7 p-1.5';
    }
  };

  const getTooltipPosition = () => {
    switch (position) {
      case 'bottom': return 'top-full mt-2 left-1/2 -translate-x-1/2';
      case 'left': return 'right-full mr-2 top-1/2 -translate-y-1/2';
      case 'right': return 'left-full ml-2 top-1/2 -translate-y-1/2';
      default: return 'bottom-full mb-2 left-1/2 -translate-x-1/2';
    }
  };

  const config = getSeverityConfig(anomaly.severity);
  const isAboveExpected = anomaly.value > anomaly.expected_range[1];
  const isBelowExpected = anomaly.value < anomaly.expected_range[0];

  return (
    <div className="relative inline-block group">
      <div
        className={`
          ${config.color} ${getSizeClasses()}
          rounded-full border-2 flex items-center justify-center
          cursor-pointer transition-transform hover:scale-110
          animate-pulse
        `}
        title={`Anomaly detected: ${config.label} severity`}
      >
        {config.icon}
      </div>

      {showDetails && (
        <div
          className={`
            absolute ${getTooltipPosition()} z-50
            w-64 p-3 bg-white border-2 ${config.color.split(' ')[2]}
            rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible
            transition-all duration-200
          `}
        >
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-gray-900">Anomaly Detected</span>
              <span className={`px-2 py-0.5 text-xs font-semibold rounded ${config.color}`}>
                {config.label}
              </span>
            </div>

            <div className="space-y-1 text-xs">
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Actual Value:</span>
                <span className="font-semibold text-gray-900">
                  {anomaly.value.toLocaleString()}
                </span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-gray-600">Expected Range:</span>
                <span className="font-medium text-gray-700">
                  {anomaly.expected_range[0].toLocaleString()} - {anomaly.expected_range[1].toLocaleString()}
                </span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-gray-600">Deviation:</span>
                <div className="flex items-center gap-1">
                  {isAboveExpected && <TrendingUp className="w-3 h-3 text-red-600" />}
                  {isBelowExpected && <TrendingDown className="w-3 h-3 text-red-600" />}
                  <span className="font-semibold text-red-600">
                    {Math.abs(anomaly.deviation).toFixed(1)}%
                  </span>
                </div>
              </div>

              {anomaly.timestamp && (
                <div className="flex items-center justify-between pt-1 border-t border-gray-200">
                  <span className="text-gray-600">Timestamp:</span>
                  <span className="font-medium text-gray-700">
                    {new Date(anomaly.timestamp).toLocaleDateString()}
                  </span>
                </div>
              )}
            </div>

            <div className="pt-2 border-t border-gray-200">
              <p className="text-xs text-gray-600">
                {isAboveExpected && 'Value is significantly higher than expected.'}
                {isBelowExpected && 'Value is significantly lower than expected.'}
              </p>
            </div>
          </div>

          <div className={`
            absolute w-2 h-2 bg-white border-2 ${config.color.split(' ')[2]}
            transform rotate-45
            ${position === 'top' ? 'top-full -mt-1.5 left-1/2 -ml-1' : ''}
            ${position === 'bottom' ? 'bottom-full -mb-1.5 left-1/2 -ml-1' : ''}
            ${position === 'left' ? 'left-full -ml-1.5 top-1/2 -mt-1' : ''}
            ${position === 'right' ? 'right-full -mr-1.5 top-1/2 -mt-1' : ''}
          `} />
        </div>
      )}
    </div>
  );
};
