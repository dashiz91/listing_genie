import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { useCredits } from '@/contexts/CreditContext';

interface OutOfCreditsModalProps {
  open: boolean;
  onClose: () => void;
  requiredCredits?: number;
}

export const OutOfCreditsModal: React.FC<OutOfCreditsModalProps> = ({
  open,
  onClose,
  requiredCredits,
}) => {
  const navigate = useNavigate();
  const { balance, planName } = useCredits();

  const handleUpgrade = () => {
    onClose();
    navigate('/app/settings?tab=billing');
  };

  return (
    <AlertDialog open={open} onOpenChange={(isOpen: boolean) => !isOpen && onClose()}>
      <AlertDialogContent className="bg-slate-900 border-slate-700">
        <AlertDialogHeader>
          <div className="mx-auto w-12 h-12 rounded-full bg-red-500/20 flex items-center justify-center mb-2">
            <svg className="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <AlertDialogTitle className="text-center text-white">
            Not Enough Credits
          </AlertDialogTitle>
          <AlertDialogDescription className="text-center text-slate-400">
            {requiredCredits ? (
              <>
                You need <span className="text-white font-semibold">{requiredCredits} credits</span> for this action,
                but you only have <span className="text-red-400 font-semibold">{balance} credits</span> remaining.
              </>
            ) : (
              <>
                You've run out of credits on your <span className="capitalize">{planName}</span> plan.
              </>
            )}
          </AlertDialogDescription>
        </AlertDialogHeader>

        <div className="my-4 p-3 bg-slate-800/50 rounded-lg border border-slate-700/50">
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-400">Current Balance</span>
            <span className="text-white font-mono">{balance} credits</span>
          </div>
          {requiredCredits && (
            <div className="flex items-center justify-between text-sm mt-2">
              <span className="text-slate-400">Required</span>
              <span className="text-red-400 font-mono">{requiredCredits} credits</span>
            </div>
          )}
        </div>

        <AlertDialogFooter className="flex-col sm:flex-row gap-2">
          <AlertDialogCancel
            onClick={onClose}
            className="bg-slate-800 border-slate-700 text-slate-300 hover:bg-slate-700 hover:text-white"
          >
            Maybe Later
          </AlertDialogCancel>
          <AlertDialogAction
            onClick={handleUpgrade}
            className="bg-redd-500 hover:bg-redd-600 text-white"
          >
            Upgrade Plan
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
};

export default OutOfCreditsModal;
