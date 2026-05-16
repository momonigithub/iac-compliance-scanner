"use client";

import { motion } from "framer-motion";
import { ArrowUpRight, Activity } from "lucide-react";

interface NavbarProps {
  onScan: () => void;
  isScanning: boolean;
  onCustomScan: () => void;
}

export function Navbar({ onScan, isScanning, onCustomScan }: NavbarProps) {
  return (
    <nav className="flex items-center justify-between py-5 px-8 w-full relative z-10">
      <div className="flex-1 hidden md:block">
        <span className="font-heading font-semibold tracking-tighter text-2xl text-foreground">IaC-SEC</span>
      </div>

      <ul className="hidden md:flex items-center gap-8 text-foreground/90 font-normal text-sm">
        <li className="cursor-pointer hover:opacity-70 transition-opacity flex items-center gap-1 group">
          Automated Security
        </li>
      </ul>

      <div className="md:hidden">
        <span className="font-heading font-semibold tracking-tighter text-xl text-foreground">IaC-SEC</span>
      </div>

      <div className="flex-1 flex justify-end gap-4">
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={onCustomScan}
          className="hidden md:flex items-center text-foreground rounded-full px-4 py-1.5 md:py-2 transition-colors liquid-glass"
        >
          <span className="text-xs md:text-sm font-normal">Scan Custom Code</span>
        </motion.button>
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={onScan}
          disabled={isScanning}
          className="flex items-center text-foreground rounded-full pl-2 pr-4 md:pr-6 py-1.5 md:py-2 gap-2 md:gap-3 transition-colors group liquid-glass border border-white/20"
        >
          <div className="bg-white/10 p-1 md:p-1.5 rounded-full flex items-center justify-center border border-white/10">
            {isScanning ? (
              <Activity className="w-4 h-4 md:w-5 md:h-5 text-foreground animate-spin" />
            ) : (
              <ArrowUpRight className="w-4 h-4 md:w-5 md:h-5 text-foreground" />
            )}
          </div>
          <span className="text-xs md:text-sm font-normal">
            {isScanning ? "Scanning..." : "Run Audit"}
          </span>
        </motion.button>
      </div>
    </nav>
  );
}
