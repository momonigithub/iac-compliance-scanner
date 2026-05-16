"use client";

import { motion } from "framer-motion";
import { ShieldCheck } from "lucide-react";
import { useEffect, useState } from "react";

export function BottomRightCorner() {
  const [dots, setDots] = useState([0, 1, 2]);

  useEffect(() => {
    const interval = setInterval(() => {
      setDots(prev => prev.map(() => Math.random()));
    }, 1500);
    return () => clearInterval(interval);
  }, []);

  return (
    <motion.div
      initial={{ y: 20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.8, delay: 0.4 }}
      className="absolute bottom-0 right-0 p-3 pt-5 pl-8 sm:p-4 sm:pt-6 sm:pl-10 md:p-6 md:pt-8 md:pl-14 rounded-tl-[1.5rem] sm:rounded-tl-[2rem] md:rounded-tl-[3.5rem] flex items-center gap-3 sm:gap-4 md:gap-6 liquid-glass"
    >
      <div className="bg-white/5 w-10 h-10 md:w-14 md:h-14 rounded-full flex items-center justify-center border border-white/10 overflow-hidden relative z-10">
         <motion.div 
           animate={{ rotate: 360 }} 
           transition={{ repeat: Infinity, duration: 8, ease: "linear" }}
           className="absolute inset-0 opacity-20"
           style={{ background: 'conic-gradient(from 0deg, transparent 0 340deg, hsl(260,87%,60%) 360deg)' }}
         />
        <ShieldCheck className="w-5 h-5 md:w-6 md:h-6 text-foreground relative z-10" />
      </div>
      
      <div className="flex flex-col min-w-[120px] relative z-10">
        <span className="text-[16px] md:text-[20px] font-normal text-foreground flex items-center gap-2">
          Live Threat Intel
        </span>
        <div className="flex items-center gap-1 mt-1">
          {dots.map((val, i) => (
             <motion.div 
               key={i}
               animate={{ height: 4 + val * 12 }}
               className="w-1 bg-white/40 rounded-full"
               transition={{ type: "spring", bounce: 0, duration: 0.5 }}
             />
          ))}
          <span className="text-[10px] md:text-[12px] font-mono text-foreground/60 ml-2 uppercase tracking-widest animate-pulse">Monitoring</span>
        </div>
      </div>
    </motion.div>
  );
}
