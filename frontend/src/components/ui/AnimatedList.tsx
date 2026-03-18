import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface Props {
  children: ReactNode[];
  className?: string;
}

export function AnimatedList({ children, className = '' }: Props) {
  return (
    <motion.div
      className={className}
      initial="hidden"
      animate="visible"
      variants={{ visible: { transition: { staggerChildren: 0.08 } } }}
    >
      {children.map((child, i) => (
        <motion.div
          key={i}
          variants={{
            hidden: { opacity: 0, y: 20 },
            visible: { opacity: 1, y: 0, transition: { duration: 0.3 } },
          }}
        >
          {child}
        </motion.div>
      ))}
    </motion.div>
  );
}
