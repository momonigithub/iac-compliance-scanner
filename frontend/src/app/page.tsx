"use client";

import { useEffect, useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Navbar } from "@/components/Navbar";
import { BottomLeftCard } from "@/components/BottomLeftCard";
import { BottomRightCorner } from "@/components/BottomRightCorner";
import { CustomScanModal } from "@/components/CustomScanModal";
import { DashboardView } from "@/components/DashboardView";
import { toast } from "sonner";
import { CheckCircle2, ShieldAlert } from "lucide-react";
import { InfrastructureMesh } from "@/components/InfrastructureMesh";

const API_URL = "http://localhost:8002/api";

export default function Hero() {
  const [isScanning, setIsScanning] = useState(false);
  const [summary, setSummary] = useState<any>(null);
  const [findings, setFindings] = useState<any[]>([]);
  const [history, setHistory] = useState<any[]>([]);
  const [showOverlay, setShowOverlay] = useState(false);
  const [isCustomModalOpen, setIsCustomModalOpen] = useState(false);
  const [view, setView] = useState<'hero' | 'dashboard'>('hero');
  const [videoOpacity, setVideoOpacity] = useState(0);
  const videoRef = useRef<HTMLVideoElement>(null);

  const fetchDashboardData = async () => {
    try {
      const summaryRes = await fetch(`${API_URL}/summary`);
      const summaryData = await summaryRes.json();
      setSummary(summaryData.detail ? null : summaryData);

      const findingsRes = await fetch(`${API_URL}/findings`);
      const findingsData = await findingsRes.json();
      setFindings(Array.isArray(findingsData) ? findingsData : []);

      const historyRes = await fetch(`${API_URL}/history`);
      const historyData = await historyRes.json();
      setHistory(Array.isArray(historyData) ? historyData : []);
    } catch (err) {
      console.error("Error fetching data:", err);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    // Initial fade in for video
    setTimeout(() => setVideoOpacity(1), 100);
  }, []);

  const runScan = async () => {
    setIsScanning(true);
    setShowOverlay(true);
    try {
      const res = await fetch(`${API_URL}/scan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
      const data = await res.json();
      await fetchDashboardData();
      
      if (data.data?.failed > 0) {
        toast.error(`Audit Complete: ${data.data.failed} Violations Found`, {
          icon: <ShieldAlert className="text-red-500" />
        });
      } else {
        toast.success("Audit Complete: Infrastructure Secure", {
          icon: <CheckCircle2 className="text-green-500" />
        });
      }
    } catch (err) {
      console.error("Scan failed:", err);
      toast.error("Audit failed to complete. Check backend logs.");
    } finally {
      setIsScanning(false);
      setTimeout(() => setShowOverlay(false), 1500);
    }
  };

  return (
    <main className="min-h-screen flex flex-col bg-background relative overflow-hidden text-foreground">
      
      {/* Blurred Overlay Shape */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[984px] h-[527px] opacity-90 bg-gray-950 blur-[82px] pointer-events-none z-0" />

      {/* Video Background */}
      <video
        ref={videoRef}
        autoPlay
        muted
        playsInline
        className="absolute inset-0 w-full h-full object-cover z-0 transition-opacity duration-500"
        style={{ opacity: videoOpacity }}
        onEnded={() => {
          setVideoOpacity(0);
          setTimeout(() => {
            if (videoRef.current) {
              videoRef.current.currentTime = 0;
              videoRef.current.play();
              setVideoOpacity(1);
            }
          }, 100);
        }}
      >
        <source src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260328_065045_c44942da-53c6-4804-b734-f9e07fc22e08.mp4" type="video/mp4" />
      </video>

      {/* Optional: 3D Mesh Overlay (Low opacity) */}
      <div className="absolute inset-0 z-0 opacity-40 pointer-events-none">
         <InfrastructureMesh findings={findings} isScanning={isScanning} />
      </div>

      {/* Scan Laser Overlay Effect */}
      <AnimatePresence>
        {showOverlay && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 z-20 bg-background/40 backdrop-blur-[2px] flex items-center justify-center pointer-events-none"
          >
            <div className="scan-line absolute top-0 left-0 right-0 h-1 bg-primary shadow-[0_0_20px_var(--color-primary)]" />
            <style jsx>{`
              .scan-line {
                animation: scan 2s linear infinite;
              }
              @keyframes scan {
                0% { top: 0; opacity: 0; }
                10% { opacity: 1; }
                90% { opacity: 1; }
                100% { top: 100%; opacity: 0; }
              }
            `}</style>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence mode="wait">
        {view === 'hero' ? (
          <motion.div 
            key="hero"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.5 }}
            className="relative z-10 flex-1 flex flex-col w-full h-full"
          >
            <Navbar onScan={runScan} isScanning={isScanning} onCustomScan={() => setIsCustomModalOpen(true)} />

            {/* Divider below navbar */}
            <div className="w-full h-[1px] bg-gradient-to-r from-transparent via-foreground/20 to-transparent mt-[3px]" />

            {/* Center Content */}
            <div className="flex-1 flex flex-col items-center justify-center px-6 text-center">
              <motion.h1
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.2 }}
                className="text-[120px] sm:text-[150px] md:text-[220px] font-normal leading-[1.02] tracking-[-0.024em]"
              >
                <span className="bg-clip-text text-transparent bg-[linear-gradient(to_left,#6366f1,#a855f7,#fcd34d)]">IaC</span>
                <span className="text-foreground"> Scanner</span>
              </motion.h1>
              
              <motion.p
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.4 }}
                className="text-[var(--hero-sub)] text-lg md:text-xl leading-8 max-w-lg mt-[9px] opacity-80 font-normal"
              >
                The most powerful SAST engine deployed <br className="hidden md:block"/> in infrastructure security.
              </motion.p>
            </div>

            {/* Corner Widgets */}
            <BottomLeftCard score={summary?.latest_score} onViewReport={() => setView('dashboard')} />
            <BottomRightCorner />
          </motion.div>
        ) : (
          <DashboardView 
            key="dashboard"
            summary={summary}
            findings={findings}
            history={history}
            onClose={() => setView('hero')}
          />
        )}
      </AnimatePresence>

      {/* Custom Scan Modal */}
      <CustomScanModal isOpen={isCustomModalOpen} onClose={() => setIsCustomModalOpen(false)} />
    </main>
  );
}
