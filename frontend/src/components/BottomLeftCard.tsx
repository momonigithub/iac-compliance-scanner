"use client";

import { motion } from "framer-motion";
import { ArrowUpRight } from "lucide-react";

export function BottomLeftCard({ score = "--", onViewReport }: { score?: string | number, onViewReport: () => void }) {
  return (
    <motion.div
      initial={{ x: -20, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.8, delay: 0.2 }}
      className="absolute bottom-28 right-4 left-auto md:left-6 md:right-auto md:bottom-6 lg:bottom-10 lg:left-10 p-3 md:p-4 lg:p-5 rounded-[1.2rem] md:rounded-[1.5rem] lg:rounded-[2.2rem] flex flex-col gap-2 lg:gap-3 min-w-[140px] md:min-w-[150px] lg:min-w-[180px] w-fit liquid-glass"
    >
      <div className="flex flex-col relative z-10">
        <span className="text-2xl md:text-3xl font-normal text-foreground tracking-tight">
          {score}%
        </span>
        <span className="text-[10px] md:text-[12px] font-normal text-foreground/60 uppercase tracking-wider">
          Compliance Score
        </span>
      </div>
      
      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        className="flex items-center bg-white/10 rounded-full pl-1.5 pr-5 py-1.5 gap-2 hover:bg-white/20 transition-colors self-start group relative z-10 border border-white/5"
        onClick={onViewReport}
      >
        <div className="bg-white/10 p-1 rounded-full flex items-center justify-center border border-white/5">
          <ArrowUpRight className="w-3.5 h-3.5 text-foreground" />
        </div>
        <span className="text-[14px] font-normal text-foreground">
          Full Report
        </span>
      </motion.button>
    </motion.div>
  );
}
