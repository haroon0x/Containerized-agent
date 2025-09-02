
import React from 'react';
import { motion } from 'framer-motion';

const SkeletonLoader = () => {
  const variants = {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
  };

  return (
    <motion.div initial="initial" animate="animate" variants={variants}>
      {[...Array(5)].map((_, i) => (
        <div key={i} className="p-3 mb-2 rounded" style={{ backgroundColor: 'var(--muted)' }}>
          <div className="d-flex justify-content-between align-items-center">
            <div style={{ width: '70%' }}>
              <div className="mb-2 rounded" style={{ height: '20px', width: '80%', backgroundColor: 'var(--border)' }}></div>
              <div className="rounded" style={{ height: '16px', width: '50%', backgroundColor: 'var(--border)' }}></div>
            </div>
            <div className="rounded" style={{ height: '30px', width: '80px', backgroundColor: 'var(--border)' }}></div>
          </div>
        </div>
      ))}
    </motion.div>
  );
};

export default SkeletonLoader;
