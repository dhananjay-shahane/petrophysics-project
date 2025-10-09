import DockablePanel from "./DockablePanel";
import { Button } from "@/components/ui/button";
import { Upload, FileText, X } from "lucide-react";
import { useState, useRef } from "react";
import { useToast } from "@/hooks/use-toast";

export default function FeedbackPanelNew({ 
  onClose,
  onMinimize,
  isFloating,
  onDock,
  onFloat,
  savedPosition,
  savedSize,
  onGeometryChange
}: { 
  onClose?: () => void;
  onMinimize?: () => void;
  isFloating?: boolean;
  onDock?: () => void;
  onFloat?: () => void;
  savedPosition?: { x: number; y: number };
  savedSize?: { width: number; height: number };
  onGeometryChange?: (pos: { x: number; y: number }, size: { width: number; height: number }) => void;
}) {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files).filter(
      file => file.name.endsWith('.csv')
    );

    if (files.length > 0) {
      setSelectedFiles(prev => [...prev, ...files]);
      toast({
        title: "Files Added",
        description: `${files.length} CSV file(s) added successfully.`,
      });
    } else {
      toast({
        title: "Invalid File Type",
        description: "Please select CSV files only.",
        variant: "destructive",
      });
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []).filter(
      file => file.name.endsWith('.csv')
    );

    if (files.length > 0) {
      setSelectedFiles(prev => [...prev, ...files]);
      toast({
        title: "Files Selected",
        description: `${files.length} CSV file(s) selected successfully.`,
      });
    }
  };

  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleSelectCSV = () => {
    fileInputRef.current?.click();
  };

  return (
    <DockablePanel 
      id="feedback" 
      title="Feedback" 
      onClose={onClose}
      onMinimize={onMinimize}
      isFloating={isFloating}
      onDock={onDock}
      onFloat={onFloat}
      savedPosition={savedPosition}
      savedSize={savedSize}
      onGeometryChange={onGeometryChange}
    >
      <div className="flex flex-col h-full p-3 gap-3">
        <div className="flex gap-2">
          <Button size="sm" variant="outline" data-testid="button-load-log">Load Log</Button>
          <Button 
            size="sm" 
            variant="outline" 
            onClick={handleSelectCSV}
            data-testid="button-load-csv"
          >
            Select CSV
          </Button>
        </div>
        
        <div 
          className={`flex-1 border-2 border-dashed rounded-lg transition-colors ${
            isDragging 
              ? 'border-primary bg-primary/10' 
              : 'border-border bg-background'
          }`}
          onDragEnter={handleDragEnter}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          {selectedFiles.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
              <Upload className="w-12 h-12 mb-3 opacity-50" />
              <p className="text-sm font-medium">Drop CSV files here</p>
              <p className="text-xs mt-1">or click "Select CSV" button</p>
            </div>
          ) : (
            <div className="p-3 overflow-auto h-full">
              <div className="text-sm font-semibold mb-2">Selected CSV Files:</div>
              <div className="space-y-2">
                {selectedFiles.map((file, index) => (
                  <div 
                    key={index}
                    className="flex items-center justify-between p-2 bg-secondary rounded border border-border"
                  >
                    <div className="flex items-center gap-2 flex-1 min-w-0">
                      <FileText className="w-4 h-4 text-primary flex-shrink-0" />
                      <span className="text-sm truncate" title={file.name}>
                        {file.name}
                      </span>
                      <span className="text-xs text-muted-foreground flex-shrink-0">
                        ({(file.size / 1024).toFixed(1)} KB)
                      </span>
                    </div>
                    <Button
                      size="icon"
                      variant="ghost"
                      className="h-6 w-6 flex-shrink-0"
                      onClick={() => removeFile(index)}
                    >
                      <X className="w-3.5 h-3.5" />
                    </Button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <input
          ref={fileInputRef}
          type="file"
          accept=".csv"
          multiple
          className="hidden"
          onChange={handleFileSelect}
        />
      </div>
    </DockablePanel>
  );
}
