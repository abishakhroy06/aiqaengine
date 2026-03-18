import { HTMLMotionProps, motion } from 'framer-motion';
import { forwardRef } from 'react';
import { cn } from '../../lib/utils';

interface Props extends Omit<HTMLMotionProps<'input'>, 'ref'> {
  label?: string;
  error?: string;
}

export const AnimatedInput = forwardRef<HTMLInputElement, Props>(
  ({ label, error, className, ...props }, ref) => (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      )}
      <motion.input
        ref={ref}
        whileFocus={{ scale: 1.01 }}
        className={cn(
          'w-full px-4 py-3 rounded-xl border-2 bg-white/80 backdrop-blur-sm outline-none transition-colors',
          error ? 'border-red-400 focus:border-red-500' : 'border-gray-200 focus:border-purple-400',
          className
        )}
        {...props}
      />
      {error && <p className="text-red-500 text-sm mt-1">{error}</p>}
    </div>
  )
);

AnimatedInput.displayName = 'AnimatedInput';
