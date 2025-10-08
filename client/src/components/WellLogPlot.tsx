import { useEffect, useRef, useState } from "react";

export default function WellLogPlot() {
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
      const labels = ["Gamma Ray", "Deep Res.", "PhiT", "Sw", "Sw (log)", "Sw (log)", "Sw (log)", "Sw (log)"];
      ctx.fillText(labels[i] || `Track ${i + 1}`, x + trackWidth / 2, 15);
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

    drawWaveform(0, "#2563eb", 40, 0.05, 0, "#2563eb");
    drawWaveform(1, "#9333ea", 35, 0.03, 50, "#9333ea");
    drawWaveform(2, "#059669", 30, 0.04, 100);
    drawWaveform(3, "#dc2626", 25, 0.06, 150);
    drawWaveform(3, "#10b981", 25, 0.055, 200);
    drawWaveform(4, "#dc2626", 30, 0.045, 0);
    drawWaveform(4, "#10b981", 30, 0.05, 100);
    drawWaveform(5, "#dc2626", 28, 0.055, 50);
    drawWaveform(5, "#10b981", 28, 0.048, 150);
    drawWaveform(6, "#dc2626", 32, 0.042, 100);
    drawWaveform(6, "#10b981", 32, 0.052, 200);
    drawWaveform(7, "#ef4444", 35, 0.038, 150, "#ef4444");

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

  }, [dimensions]);

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
