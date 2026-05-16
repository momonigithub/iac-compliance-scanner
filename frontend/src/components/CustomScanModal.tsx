"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Editor from "@monaco-editor/react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Activity, X, ShieldAlert, CheckCircle2, ScanLine, GripVertical } from "lucide-react";
import { toast } from "sonner";
import { Panel, PanelGroup, PanelResizeHandle } from "react-resizable-panels";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

const API_URL = "http://localhost:8002/api";

interface CustomScanModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function CustomScanModal({ isOpen, onClose }: CustomScanModalProps) {
  const [code, setCode] = useState<string>('resource "aws_s3_bucket" "example" {\n  bucket = "my-bucket"\n  acl    = "public-read"\n}\n');
  const [isScanning, setIsScanning] = useState(false);
  const [findings, setFindings] = useState<any[] | null>(null);

  const handleScan = async () => {
    setIsScanning(true);
    setFindings(null);
    try {
      const res = await fetch(`${API_URL}/scan/custom`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code }),
      });
      
      if (!res.ok) {
        throw new Error("Failed to scan code");
      }

      const data = await res.json();
      const newFindings = data.data.findings || [];
      setFindings(newFindings);

      const failedCount = newFindings.filter((f: any) => !f.passed).length;
      if (failedCount > 0) {
        toast.error(`Analysis Complete: ${failedCount} Violations Found`, {
          icon: <ShieldAlert className="text-red-500" />
        });
      } else {
        toast.success("Analysis Complete: Code is Secure", {
          icon: <CheckCircle2 className="text-green-500" />
        });
      }
    } catch (err) {
      console.error(err);
      toast.error("Failed to analyze code. Please try again.");
    } finally {
      setIsScanning(false);
    }
  };

  const getSeverityColor = (sev: string) => {
    switch (sev) {
      case "CRITICAL": return "text-red-500 border-red-500/50 bg-red-500/10";
      case "HIGH": return "text-orange-500 border-orange-500/50 bg-orange-500/10";
      case "MEDIUM": return "text-yellow-500 border-yellow-500/50 bg-yellow-500/10";
      default: return "text-blue-500 border-blue-500/50 bg-blue-500/10";
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center p-4 md:p-8 bg-black/60 backdrop-blur-md"
        >
          <motion.div
            initial={{ scale: 0.95, y: 20 }}
            animate={{ scale: 1, y: 0 }}
            exit={{ scale: 0.95, y: 20 }}
            className="w-full max-w-7xl h-full max-h-[90vh] rounded-[2rem] shadow-2xl flex flex-col overflow-hidden relative liquid-glass border border-white/10"
          >
            {/* Header */}
            <div className="flex justify-between items-center p-6 border-b border-white/10 relative z-10">
              <div>
                <h2 className="text-2xl font-heading text-foreground">Custom Code Analysis</h2>
                <p className="font-mono text-xs text-foreground/60 uppercase tracking-widest mt-1">Ephemeral Sandbox Environment</p>
              </div>
              <button 
                onClick={onClose}
                className="p-2 rounded-full hover:bg-white/10 transition-colors text-foreground"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* Body with Resizable Panels */}
            <div className="flex-1 overflow-hidden relative z-10">
              <PanelGroup direction="horizontal">
                {/* Editor Side */}
                <Panel defaultSize={50} minSize={30}>
                  <div className="flex flex-col h-full border-r border-white/10">
                    <div className="p-4 bg-black/60 flex justify-between items-center border-b border-white/20">
                      <span className="font-mono text-xs text-white/80 font-bold">main.tf</span>
                      <Button 
                        onClick={handleScan} 
                        disabled={isScanning || !code.trim()}
                        size="sm"
                        className="bg-white/10 text-white hover:bg-white/20 rounded-full h-8 border border-white/20"
                      >
                        {isScanning ? (
                          <span className="flex items-center gap-2"><Activity className="w-3 h-3 animate-spin" /> Analyzing...</span>
                        ) : (
                          <span className="flex items-center gap-2"><ScanLine className="w-3 h-3" /> Run Analysis</span>
                        )}
                      </Button>
                    </div>
                    <div className="flex-1 relative">
                      {isScanning && (
                        <div className="absolute inset-0 z-10 bg-black/60 backdrop-blur-[2px] pointer-events-none" />
                      )}
                      <Editor
                        height="100%"
                        defaultLanguage="hcl"
                        theme="vs-dark"
                        value={code}
                        onChange={(val) => {
                          if (val !== undefined) setCode(val);
                        }}
                        options={{
                          minimap: { enabled: false },
                          fontSize: 14,
                          padding: { top: 16, bottom: 16 },
                          fontFamily: "var(--font-mono)",
                        }}
                      />
                    </div>
                  </div>
                </Panel>

                {/* Resizable Divider Handle */}
                <PanelResizeHandle className="w-2 flex items-center justify-center bg-white/5 hover:bg-white/10 transition-colors group relative">
                  <div className="absolute inset-y-0 w-[1px] bg-white/10 group-hover:bg-white/20" />
                  <div className="z-10 bg-white/10 p-0.5 rounded-full border border-white/10 text-white/40 group-hover:text-white/80 transition-colors">
                    <GripVertical className="w-4 h-4" />
                  </div>
                </PanelResizeHandle>

                {/* Results Side */}
                <Panel defaultSize={50} minSize={20}>
                  <div className="h-full bg-black/40 flex flex-col overflow-hidden">
                    <div className="p-4 border-b border-white/20 flex justify-between items-center bg-black/60">
                      <h3 className="font-mono text-sm text-white font-bold flex items-center gap-2 uppercase tracking-widest">
                        <ScanLine className="w-4 h-4" /> Analysis Results
                      </h3>
                      {findings && (
                        <Badge variant="outline" className="font-mono text-[10px] bg-red-500/20 border-red-500/50 text-red-200">
                          {findings.filter((f: any) => !f.passed).length} Violations
                        </Badge>
                      )}
                    </div>
                    <ScrollArea className="flex-1 min-h-0 bg-black/20 h-full w-full">
                      {!findings ? (
                        <div className="flex flex-col items-center justify-center h-full text-white/30 p-12 text-center">
                          <Activity className="w-12 h-12 mb-4 opacity-20" />
                          <p className="font-mono text-sm">Enter code and click "Run Analysis" to see results.</p>
                        </div>
                      ) : findings.filter((f: any) => !f.passed).length === 0 ? (
                        <div className="flex flex-col items-center justify-center h-full text-white py-20">
                          <CheckCircle2 className="w-16 h-16 text-green-400 mb-4 opacity-90" />
                          <p className="font-mono text-base font-semibold">No vulnerabilities detected.</p>
                        </div>
                      ) : (
                        <Table>
                          <TableHeader className="bg-black/80 sticky top-0 z-10 border-b border-white/20">
                            <TableRow className="border-none hover:bg-transparent">
                              <TableHead className="font-mono text-xs text-white/90 font-bold py-4">Severity</TableHead>
                              <TableHead className="font-mono text-xs text-white/90 font-bold py-4">Check ID</TableHead>
                              <TableHead className="font-mono text-xs text-white/90 font-bold py-4">Resource</TableHead>
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            {findings.filter((f: any) => !f.passed).map((finding: any, idx: number) => (
                              <TableRow key={idx} className="border-b border-white/10 hover:bg-white/10 transition-colors">
                                <TableCell className="py-4">
                                  <span className={`px-2 py-1 rounded text-[10px] font-bold font-mono border ${getSeverityColor(finding.severity)}`}>
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
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      )}
                    </ScrollArea>
                  </div>
                </Panel>
              </PanelGroup>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
