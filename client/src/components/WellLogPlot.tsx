import { useEffect, useRef, useState } from "react";
import type { WellData } from "./AdvancedDockWorkspace";

interface WellLogPlotProps {
  selectedWell?: WellData | null;
}

export default function WellLogPlot({ selectedWell }: WellLogPlotProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 1200, height: 800 });

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const updateDimensions = () => {
      const rect = container.getBoundingClientRect();
      const maxWidth = 2400;
      const maxHeight = 1600;
      const minWidth = 600;
      const minHeight = 400;
      
      setDimensions({
        width: Math.min(maxWidth, Math.max(minWidth, rect.width - 32)),
        height: Math.min(maxHeight, Math.max(minHeight, rect.height - 32)),
      });
    };

    updateDimensions();

    const resizeObserver = new ResizeObserver(updateDimensions);
    resizeObserver.observe(container);

    return () => {
      resizeObserver.disconnect();
    };
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const width = dimensions.width;
    const height = dimensions.height;

    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, width, height);

    // Show message if no well is selected
    if (!selectedWell) {
      ctx.fillStyle = "#999999";
      ctx.font = "16px sans-serif";
      ctx.textAlign = "center";
      ctx.fillText("No well selected", width / 2, height / 2);
      ctx.font = "14px sans-serif";
      ctx.fillText("Select a well from the Wells panel to display the log plot", width / 2, height / 2 + 25);
      return;
    }

    // Show loading message if well data is not loaded yet
    if (!selectedWell.data || !Array.isArray(selectedWell.data) || selectedWell.data.length === 0) {
      ctx.fillStyle = "#999999";
      ctx.font = "16px sans-serif";
      ctx.textAlign = "center";
      ctx.fillText(`Loading well: ${selectedWell.name}...`, width / 2, height / 2);
      return;
    }

    ctx.strokeStyle = "#cccccc";
    ctx.lineWidth = 1;

    for (let x = 0; x < width; x += 50) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }

    for (let y = 0; y < height; y += 50) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

    const trackWidth = Math.max(100, width / 12);
    const numTracks = 8;
    const startX = Math.max(80, trackWidth * 0.8);

    // Get curve names from well data
    const curves = selectedWell.logs || [];
    const displayCurves = curves.filter((c: string) => c !== 'DEPT' && c !== 'DEPTH'); // Exclude depth from display curves
    const numDisplayTracks = Math.min(displayCurves.length, numTracks);

    for (let i = 0; i < numTracks; i++) {
      const x = startX + i * trackWidth;
      
      ctx.strokeStyle = "#333333";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();

      ctx.fillStyle = "#333333";
      ctx.font = "12px sans-serif";
      ctx.textAlign = "center";
      const label = i < displayCurves.length ? displayCurves[i] : `Track ${i + 1}`;
      ctx.fillText(label, x + trackWidth / 2, 15);
    }

    const drawWaveform = (
      trackIndex: number,
      color: string,
      amplitude: number,
      frequency: number,
      offset: number = 0,
      fillColor?: string
    ) => {
      const x = startX + trackIndex * trackWidth;
      const centerX = x + trackWidth / 2;

      ctx.strokeStyle = color;
      ctx.lineWidth = 1.5;
      ctx.beginPath();

      for (let y = 30; y < height; y += 2) {
        const value = Math.sin((y + offset) * frequency) * (amplitude * trackWidth / 120);
        const px = centerX + value;
        if (y === 30) {
          ctx.moveTo(px, y);
        } else {
          ctx.lineTo(px, y);
        }
      }
      ctx.stroke();

      if (fillColor) {
        ctx.fillStyle = fillColor;
        ctx.globalAlpha = 0.3;
        ctx.beginPath();
        ctx.moveTo(x, 30);
        for (let y = 30; y < height; y += 2) {
          const value = Math.sin((y + offset) * frequency) * (amplitude * trackWidth / 120);
          const px = centerX + value;
          ctx.lineTo(px, y);
        }
        ctx.lineTo(x, height);
        ctx.closePath();
        ctx.fill();
        ctx.globalAlpha = 1.0;
      }
    };

    // Draw real well log data
    const wellData = selectedWell.data;
    const depthKey = curves.find((c: string) => c === 'DEPT' || c === 'DEPTH') || 'DEPT';
    const colors = ["#2563eb", "#9333ea", "#059669", "#dc2626", "#10b981", "#f59e0b", "#8b5cf6", "#ef4444"];
    
    // Get depth range for scaling
    const depths = wellData.map((d: any) => d[depthKey] || 0);
    const minDepth = Math.min(...depths);
    const maxDepth = Math.max(...depths);
    const depthRange = maxDepth - minDepth;
    
    // Draw each curve
    displayCurves.forEach((curveName: string, trackIndex: number) => {
      if (trackIndex >= numTracks) return;
      
      const x = startX + trackIndex * trackWidth;
      const centerX = x + trackWidth / 2;
      const color = colors[trackIndex % colors.length];
      
      // Get min/max for this curve to normalize
      const values = wellData.map((d: any) => d[curveName] || 0).filter((v: number) => isFinite(v));
      if (values.length === 0) return;
      
      const minVal = Math.min(...values);
      const maxVal = Math.max(...values);
      const range = maxVal - minVal || 1;
      
      ctx.strokeStyle = color;
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      
      wellData.forEach((dataPoint: any, index: number) => {
        const depth = dataPoint[depthKey];
        const value = dataPoint[curveName];
        
        if (!isFinite(depth) || !isFinite(value)) return;
        
        // Scale depth to canvas y
        const y = 30 + ((depth - minDepth) / depthRange) * (height - 60);
        
        // Scale value to track width (normalize to -1 to 1 range, then to pixels)
        const normalizedValue = (value - minVal) / range; // 0 to 1
        const px = centerX + (normalizedValue - 0.5) * (trackWidth * 0.8); // Center and scale
        
        if (index === 0) {
          ctx.moveTo(px, y);
        } else {
          ctx.lineTo(px, y);
        }
      });
      
      ctx.stroke();
    });

    const zonationScale = height / 800;
    const zonations = [
      { y: 150 * zonationScale, label: "CLEAR FORK" },
      { y: 280 * zonationScale, label: "SPRABERRY" },
      { y: 380 * zonationScale, label: "Mid_SPRB" },
      { y: 480 * zonationScale, label: "WOLFCAMP B" },
      { y: 550 * zonationScale, label: "WOLFCAMP C" },
      { y: 650 * zonationScale, label: "WOLFCAMP D" },
      { y: 720 * zonationScale, label: "Base" },
    ];

    ctx.strokeStyle = "#000000";
    ctx.lineWidth = 1;
    ctx.fillStyle = "#000000";
    ctx.font = "11px sans-serif";
    ctx.textAlign = "right";

    zonations.forEach((zone) => {
      ctx.beginPath();
      ctx.moveTo(startX, zone.y);
      ctx.lineTo(startX + numTracks * trackWidth, zone.y);
      ctx.stroke();

      ctx.fillText(zone.label, startX + numTracks * trackWidth + 80, zone.y + 4);
    });

  }, [dimensions, selectedWell]);

  return (
    <div ref={containerRef} className="w-full h-full overflow-auto bg-white p-4 max-w-[2400px] max-h-[1600px]">
      <canvas
        ref={canvasRef}
        width={dimensions.width}
        height={dimensions.height}
        className="border border-gray-300 w-full h-full"
        style={{ maxWidth: dimensions.width, maxHeight: dimensions.height }}
        data-testid="canvas-welllog"
      />
    </div>
  );
}
