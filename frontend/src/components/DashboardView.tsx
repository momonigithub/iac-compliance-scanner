"use client";

import { motion } from "framer-motion";
import { ArrowLeft, ShieldAlert, CheckCircle2 } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

interface DashboardViewProps {
  summary: any;
  findings: any[];
  history: any[];
  onClose: () => void;
}

export function DashboardView({ summary, findings, history, onClose }: DashboardViewProps) {
  const getSeverityColor = (sev: string) => {
    switch (sev) {
      case "CRITICAL": return "text-red-400 border-red-500/80 bg-red-500/20";
      case "HIGH": return "text-orange-400 border-orange-500/80 bg-orange-500/20";
      case "MEDIUM": return "text-yellow-400 border-yellow-500/80 bg-yellow-500/20";
      default: return "text-blue-400 border-blue-500/80 bg-blue-500/20";
    }
  };

  const getSeverityCounts = () => {
    const counts = { CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0 };
    (findings || []).forEach(f => {
      if (!f.passed && counts[f.severity as keyof typeof counts] !== undefined) {
        counts[f.severity as keyof typeof counts]++;
      }
    });
    return counts;
  };

  const sevCounts = getSeverityCounts();
  const totalFailed = (findings || []).filter(f => !f.passed).length;

  return (
    <motion.div 
      initial={{ opacity: 0, y: 50, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 20, scale: 0.95 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className="absolute inset-0 z-30 flex flex-col p-6 md:p-12 overflow-hidden bg-black/40 backdrop-blur-sm"
    >
      <div className="w-full max-w-7xl mx-auto h-full flex flex-col gap-6">
        
        {/* Header */}
        <div className="flex justify-between items-center bg-black/40 border border-white/20 rounded-2xl p-4 liquid-glass">
          <button 
            onClick={onClose}
            className="flex items-center gap-2 text-white hover:text-white/80 transition-colors font-semibold"
          >
            <ArrowLeft className="w-5 h-5" /> Back to Home
          </button>
          <div className="text-center">
            <h2 className="text-2xl font-heading text-white tracking-wide">Compliance Overview</h2>
          </div>
          <div className="w-32 text-right">
            <Badge variant="outline" className="font-mono text-sm bg-primary/40 text-white border-primary/50 py-1 px-3">
              {summary?.latest_score ?? "--"}% Score
            </Badge>
          </div>
        </div>

        {/* Top Metrics Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
          <div className="p-6 flex flex-col gap-2 liquid-glass bg-black/40 border border-white/20 rounded-2xl drop-shadow-xl">
            <span className="text-xs font-mono uppercase tracking-widest text-white/90 font-semibold">Passed</span>
            <span className="text-5xl font-heading text-green-400 drop-shadow-md">{summary?.latest_passed ?? 0}</span>
          </div>
          <div className="p-6 flex flex-col gap-2 liquid-glass bg-black/40 border border-white/20 rounded-2xl drop-shadow-xl">
            <span className="text-xs font-mono uppercase tracking-widest text-white/90 font-semibold">Failed</span>
            <span className="text-5xl font-heading text-red-400 drop-shadow-md">{summary?.latest_failed ?? 0}</span>
          </div>
          <div className="p-6 flex flex-col gap-2 liquid-glass bg-black/40 border border-white/20 rounded-2xl drop-shadow-xl">
            <span className="text-xs font-mono uppercase tracking-widest text-white/90 font-semibold">Total Checks</span>
            <span className="text-5xl font-heading text-blue-400 drop-shadow-md">{summary?.latest_total ?? 0}</span>
          </div>
          <div className="p-6 flex flex-col gap-2 liquid-glass bg-black/40 border border-white/20 rounded-2xl drop-shadow-xl">
            <span className="text-xs font-mono uppercase tracking-widest text-white/90 font-semibold">Total Scans</span>
            <span className="text-5xl font-heading text-purple-400 drop-shadow-md">{summary?.total_scans ?? 0}</span>
          </div>
        </div>

        <div className="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-6 overflow-hidden min-h-0">
          
          {/* History Trend Panel */}
          <div className="lg:col-span-1 flex flex-col gap-6 overflow-hidden min-h-0">
            <div className="p-6 flex-1 liquid-glass bg-black/40 border border-white/20 rounded-2xl flex flex-col drop-shadow-2xl overflow-hidden min-h-0">
              <h3 className="text-sm font-mono uppercase tracking-widest text-white font-bold mb-4 shrink-0">Historical Trend</h3>
              <ScrollArea className="flex-1 min-h-0 pr-4 h-full w-full">
                <div className="flex flex-col gap-3">
                  {(history || []).map((run, i) => (
                    <div key={i} className="flex justify-between items-center p-3 rounded-xl bg-black/40 border border-white/10 hover:bg-white/10 transition-colors">
                      <div className="flex flex-col">
                        <span className="text-sm font-mono text-white font-medium">{new Date(run.timestamp).toLocaleDateString()}</span>
                        <span className="text-xs text-white/70">{new Date(run.timestamp).toLocaleTimeString()}</span>
                      </div>
                      <Badge variant="outline" className={`font-mono text-xs ${run.compliance_score >= 80 ? 'text-green-300 border-green-400/50 bg-green-500/10' : run.compliance_score >= 50 ? 'text-yellow-300 border-yellow-400/50 bg-yellow-500/10' : 'text-red-300 border-red-400/50 bg-red-500/10'}`}>
                        {run.compliance_score}%
                      </Badge>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </div>
          </div>

          {/* Findings Table Panel */}
          <div className="lg:col-span-2 flex flex-col overflow-hidden liquid-glass bg-black/40 rounded-2xl border border-white/20 drop-shadow-2xl min-h-0">
            <div className="p-5 border-b border-white/20 flex justify-between items-center bg-black/50 shrink-0">
              <h3 className="font-mono text-sm text-white font-bold flex items-center gap-2 uppercase tracking-widest">
                Active Violations ({totalFailed})
              </h3>
              <div className="flex gap-2">
                <Badge className="bg-red-500/30 text-red-200 border border-red-500/50">{sevCounts.CRITICAL} CRIT</Badge>
                <Badge className="bg-orange-500/30 text-orange-200 border border-orange-500/50">{sevCounts.HIGH} HIGH</Badge>
              </div>
            </div>
            
            <ScrollArea className="flex-1 min-h-0 bg-black/20 h-full w-full">
              {totalFailed === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-white py-20">
                  <CheckCircle2 className="w-16 h-16 text-green-400 mb-4" />
                  <p className="font-mono text-base font-semibold">System Secure. No active violations.</p>
                </div>
              ) : (
                <Table>
                  <TableHeader className="bg-black/80 sticky top-0 z-10 backdrop-blur-xl border-b border-white/20">
                    <TableRow className="border-none hover:bg-transparent">
                      <TableHead className="font-mono text-xs text-white/90 font-bold py-4">Severity</TableHead>
                      <TableHead className="font-mono text-xs text-white/90 font-bold py-4">Check ID</TableHead>
                      <TableHead className="font-mono text-xs text-white/90 font-bold py-4">Resource</TableHead>
                      <TableHead className="font-mono text-xs text-white/90 font-bold py-4 text-right">Tool</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {(findings || []).filter(f => !f.passed).map((finding, idx) => (
                      <TableRow key={idx} className="border-b border-white/10 hover:bg-white/10 transition-colors">
                        <TableCell className="py-4">
                          <span className={`px-2 py-1 rounded text-xs font-bold font-mono border ${getSeverityColor(finding.severity)}`}>
                            {finding.severity}
                          </span>
                        </TableCell>
                        <TableCell className="font-mono text-sm text-white py-4">
                          <span className="font-bold">{finding.check_id}</span>
                          <div className="text-xs text-white/80 mt-1 max-w-sm" title={finding.check_name}>
                            {finding.check_name}
                          </div>
                        </TableCell>
                        <TableCell className="font-mono text-sm text-blue-300 font-semibold py-4">
                          {finding.resource}
                        </TableCell>
                        <TableCell className="text-right font-mono text-xs text-white/70 uppercase py-4">
                          {finding.tool}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </ScrollArea>
          </div>
          
        </div>
      </div>
    </motion.div>
  );
}
