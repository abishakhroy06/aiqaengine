import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface Props {
  children: ReactNode;
  className?: string;
}

export function GlassCard({ children, className = '' }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.01, y: -3 }}
      transition={{ duration: 0.2 }}
      className={`p-6 rounded-2xl bg-white/80 backdrop-blur-lg border border-white/40 shadow-xl ${className}`}
    >
      {children}
    </motion.div>
  );
}
