import React from 'react';
import { cn } from '@/lib/utils';

export interface WorkflowStep {
  id: string;
  label: string;
  status: 'pending' | 'active' | 'complete' | 'skipped';
  detail?: string;
}

interface WorkflowStepperProps {
  steps: WorkflowStep[];
  className?: string;
}

export const WorkflowStepper: React.FC<WorkflowStepperProps> = ({ steps, className }) => {
  // Don't render if nothing is active or complete
  const hasActivity = steps.some(s => s.status === 'active' || s.status === 'complete');
  if (!hasActivity) return null;

  return (
    <div className={cn('flex items-center justify-center gap-0 py-3 px-4', className)}>
      {steps.map((step, i) => {
        const isLast = i === steps.length - 1;

        // Connector line color: filled if current step is complete
        const connectorFilled = step.status === 'complete';

        return (
          <React.Fragment key={step.id}>
            {/* Step dot + label */}
            <div className="flex flex-col items-center relative">
              {/* Dot */}
              <div
                className={cn(
                  'w-3 h-3 rounded-full border-2 transition-all duration-300 flex items-center justify-center',
                  step.status === 'complete' && 'bg-redd-500 border-redd-500',
                  step.status === 'active' && 'border-redd-500 bg-redd-500 animate-pulse-soft',
                  step.status === 'pending' && 'border-slate-600 bg-transparent',
                  step.status === 'skipped' && 'border-slate-600 bg-transparent',
                )}
              >
                {step.status === 'complete' && (
                  <svg className="w-2 h-2 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                )}
              </div>

              {/* Label */}
              <span
                className={cn(
                  'text-[10px] mt-1 whitespace-nowrap font-medium transition-colors',
                  step.status === 'active' && 'text-redd-400',
                  step.status === 'complete' && 'text-slate-400',
                  step.status === 'pending' && 'text-slate-600',
                  step.status === 'skipped' && 'text-slate-600',
                )}
              >
                {step.label}
              </span>

              {/* Detail text (only on active step) */}
              {step.status === 'active' && step.detail && (
                <span className="text-[9px] text-slate-500 whitespace-nowrap absolute top-[38px]">
                  {step.detail}
                </span>
              )}
            </div>

            {/* Connector line */}
            {!isLast && (
              <div
                className={cn(
                  'h-[2px] w-12 sm:w-16 mx-1 transition-colors duration-300 -mt-4',
                  connectorFilled ? 'bg-redd-500' : 'bg-slate-700',
                )}
              />
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
};
