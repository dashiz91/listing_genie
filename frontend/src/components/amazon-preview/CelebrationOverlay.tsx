import React, { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';

interface CelebrationOverlayProps {
  isVisible: boolean;
  onComplete?: () => void;
  message?: string;
  subMessage?: string;
}

// Simple confetti particle
interface Particle {
  id: number;
  x: number;
  y: number;
  color: string;
  rotation: number;
  scale: number;
  velocityX: number;
  velocityY: number;
}

const COLORS = ['#C85A35', '#D4795A', '#22C55E', '#3B82F6', '#A855F7', '#F59E0B'];

export const CelebrationOverlay: React.FC<CelebrationOverlayProps> = ({
  isVisible,
  onComplete,
  message = 'Saved!',
  subMessage = 'Your project has been saved to Projects',
}) => {
  const [particles, setParticles] = useState<Particle[]>([]);
  const [showMessage, setShowMessage] = useState(false);

  // Generate particles when visible
  useEffect(() => {
    if (isVisible) {
      // Create confetti particles
      const newParticles: Particle[] = [];
      for (let i = 0; i < 50; i++) {
        newParticles.push({
          id: i,
          x: Math.random() * 100,
          y: -10 - Math.random() * 20,
          color: COLORS[Math.floor(Math.random() * COLORS.length)],
          rotation: Math.random() * 360,
          scale: 0.5 + Math.random() * 0.5,
          velocityX: (Math.random() - 0.5) * 3,
          velocityY: 2 + Math.random() * 3,
        });
      }
      setParticles(newParticles);
      setShowMessage(true);

      // Auto-dismiss after 2.5 seconds
      const timer = setTimeout(() => {
        setShowMessage(false);
        setParticles([]);
        onComplete?.();
      }, 2500);

      return () => clearTimeout(timer);
    }
  }, [isVisible, onComplete]);

  if (!isVisible && particles.length === 0) return null;

  return (
    <div
      className={cn(
        'fixed inset-0 z-50 pointer-events-none overflow-hidden',
        'transition-opacity duration-300',
        isVisible ? 'opacity-100' : 'opacity-0'
      )}
    >
      {/* Confetti particles */}
      {particles.map((particle) => (
        <div
          key={particle.id}
          className="absolute w-3 h-3 rounded-sm animate-confetti-fall"
          style={{
            left: `${particle.x}%`,
            top: `${particle.y}%`,
            backgroundColor: particle.color,
            transform: `rotate(${particle.rotation}deg) scale(${particle.scale})`,
            animationDelay: `${particle.id * 20}ms`,
            animationDuration: '2s',
          }}
        />
      ))}

      {/* Success message badge */}
      {showMessage && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div
            className={cn(
              'px-8 py-6 bg-slate-800/95 backdrop-blur-sm rounded-2xl border border-slate-600',
              'shadow-2xl shadow-redd-500/20',
              'animate-bounce-in'
            )}
          >
            {/* Success icon */}
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-green-500/20 flex items-center justify-center">
              <svg
                className="w-10 h-10 text-green-500 animate-check-draw"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2.5}
                  d="M5 13l4 4L19 7"
                />
              </svg>
            </div>

            {/* Message */}
            <h3 className="text-2xl font-bold text-white text-center mb-1">
              {message}
            </h3>
            <p className="text-slate-400 text-center text-sm">
              {subMessage}
            </p>
          </div>
        </div>
      )}

      {/* CSS Animations */}
      <style>{`
        @keyframes confetti-fall {
          0% {
            transform: translateY(0) rotate(0deg);
            opacity: 1;
          }
          100% {
            transform: translateY(100vh) rotate(720deg);
            opacity: 0;
          }
        }

        @keyframes bounce-in {
          0% {
            transform: scale(0.3);
            opacity: 0;
          }
          50% {
            transform: scale(1.05);
          }
          70% {
            transform: scale(0.95);
          }
          100% {
            transform: scale(1);
            opacity: 1;
          }
        }

        @keyframes check-draw {
          0% {
            stroke-dasharray: 0 100;
          }
          100% {
            stroke-dasharray: 100 0;
          }
        }

        .animate-confetti-fall {
          animation: confetti-fall 2s ease-out forwards;
        }

        .animate-bounce-in {
          animation: bounce-in 0.5s ease-out forwards;
        }

        .animate-check-draw {
          stroke-dasharray: 100;
          animation: check-draw 0.5s ease-out 0.2s forwards;
        }
      `}</style>
    </div>
  );
};
