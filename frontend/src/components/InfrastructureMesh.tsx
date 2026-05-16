"use client";

import { useRef, useMemo, useState } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Html, Sphere, Stars } from "@react-three/drei";
import * as THREE from "three";
import { Badge } from "./ui/badge";
import { Card } from "./ui/card";

// Dummy data structure if no actual findings are passed
const DUMMY_NODES = Array.from({ length: 30 }).map((_, i) => ({
  id: i,
  status: Math.random() > 0.8 ? "failed" : "passed",
  severity: Math.random() > 0.5 ? "HIGH" : "MEDIUM",
  resource: `aws_resource_${i}`,
  position: new THREE.Vector3(
    (Math.random() - 0.5) * 15,
    (Math.random() - 0.5) * 15,
    (Math.random() - 0.5) * 15
  ),
}));

function Node({ data, isScanning }: { data: any; isScanning: boolean }) {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHover] = useState(false);

  // Colors based on status
  const color = data.status === "failed" 
    ? (data.severity === "CRITICAL" || data.severity === "HIGH" ? "#ff4d4d" : "#f5c518")
    : "#39d98a";

  useFrame((state) => {
    if (!meshRef.current) return;
    
    // Gentle floating animation
    const t = state.clock.getElapsedTime();
    meshRef.current.position.y += Math.sin(t + data.id) * 0.005;
    
    // Pulse if scanning or hovered
    if (isScanning || hovered) {
      const scale = 1 + Math.sin(t * 5 + data.id) * 0.2;
      meshRef.current.scale.set(scale, scale, scale);
    } else {
      meshRef.current.scale.set(1, 1, 1);
    }
  });

  return (
    <Sphere
      ref={meshRef}
      args={[0.2, 16, 16]}
      position={data.position}
      onPointerOver={() => setHover(true)}
      onPointerOut={() => setHover(false)}
    >
      <meshStandardMaterial 
        color={color} 
        emissive={color}
        emissiveIntensity={hovered ? 2 : 0.5}
        toneMapped={false} 
      />
      
      {/* HTML Tooltip on hover */}
      {hovered && (
        <Html distanceFactor={10} zIndexRange={[100, 0]}>
          <Card className="w-64 p-3 bg-black/80 backdrop-blur-md border-white/10 text-xs shadow-2xl">
            <div className="flex justify-between items-start mb-2">
              <span className="font-mono text-white/50">{data.tool || 'checkov'}</span>
              <Badge variant={data.status === "failed" ? "destructive" : "default"} className="text-[10px] uppercase">
                {data.severity || 'OK'}
              </Badge>
            </div>
            <p className="font-heading font-medium text-white mb-1 truncate">{data.resource}</p>
            {data.check_name && (
              <p className="text-white/70 truncate">{data.check_name}</p>
            )}
          </Card>
        </Html>
      )}
    </Sphere>
  );
}

function Connections({ nodes }: { nodes: any[] }) {
  const lines = useMemo(() => {
    const arr = [];
    // Create random connections between nodes to look like a mesh
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        if (nodes[i].position.distanceTo(nodes[j].position) < 5) {
          arr.push(nodes[i].position, nodes[j].position);
        }
      }
    }
    return new THREE.BufferGeometry().setFromPoints(arr);
  }, [nodes]);

  return (
    <lineSegments geometry={lines}>
      <lineBasicMaterial color="#ffffff" transparent opacity={0.1} />
    </lineSegments>
  );
}

export function InfrastructureMesh({ findings = [], isScanning = false }) {
  // Map real findings to 3D nodes if available, else use dummy data
  const nodes = useMemo(() => {
    const safeFindings = Array.isArray(findings) ? findings : [];
    if (safeFindings.length === 0) return DUMMY_NODES;
    
    // Take up to 50 findings to avoid overwhelming the canvas
    return safeFindings.slice(0, 50).map((f: any, i: number) => ({
      ...f,
      id: i,
      status: f.passed ? "passed" : "failed",
      position: new THREE.Vector3(
        (Math.random() - 0.5) * 15,
        (Math.random() - 0.5) * 15,
        (Math.random() - 0.5) * 15
      ),
    }));
  }, [findings]);

  return (
    <div className="absolute inset-0 z-0 pointer-events-auto">
      <Canvas camera={{ position: [0, 0, 15], fov: 60 }}>
        <ambientLight intensity={0.2} />
        <pointLight position={[10, 10, 10]} intensity={1} />
        
        <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
        
        <group rotation={[0.2, 0.5, 0]}>
          <Connections nodes={nodes} />
          {nodes.map((node) => (
            <Node key={node.id} data={node} isScanning={isScanning} />
          ))}
        </group>
      </Canvas>
    </div>
  );
}
