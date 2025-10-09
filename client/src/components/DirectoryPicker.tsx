import { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Folder, ChevronRight, Home, ArrowUp } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface DirectoryPickerProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSelectPath: (path: string) => void;
  initialPath?: string;
}

interface Directory {
  name: string;
  path: string;
}

interface DirectoryResponse {
  currentPath: string;
  parentPath: string;
  directories: Directory[];
}

export default function DirectoryPicker({
  open,
  onOpenChange,
  onSelectPath,
  initialPath = "/home/runner/workspace",
}: DirectoryPickerProps) {
  const [currentPath, setCurrentPath] = useState(initialPath);
  const [parentPath, setParentPath] = useState("");
  const [directories, setDirectories] = useState<Directory[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const loadDirectories = async (path: string) => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/directories/list?path=${encodeURIComponent(path)}`);
      
      if (!response.ok) {
        throw new Error("Failed to load directories");
      }

      const data: DirectoryResponse = await response.json();
      setCurrentPath(data.currentPath);
      setParentPath(data.parentPath);
      setDirectories(data.directories);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load directories",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (open) {
      loadDirectories(currentPath);
    }
  }, [open]);

  const handleSelectDirectory = (dirPath: string) => {
    loadDirectories(dirPath);
  };

  const handleGoUp = () => {
    if (parentPath) {
      loadDirectories(parentPath);
    }
  };

  const handleGoHome = () => {
    loadDirectories("/home/runner/workspace");
  };

  const handleConfirm = () => {
    onSelectPath(currentPath);
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Choose Directory Path</DialogTitle>
          <DialogDescription>
            Browse and select the directory where you want to create your project
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleGoHome}
              disabled={isLoading}
              title="Go to workspace"
            >
              <Home className="w-4 h-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleGoUp}
              disabled={isLoading || !parentPath || currentPath === parentPath}
              title="Go up one level"
            >
              <ArrowUp className="w-4 h-4" />
            </Button>
            <div className="flex-1 px-3 py-2 bg-muted rounded-md font-mono text-sm truncate">
              {currentPath}
            </div>
          </div>

          <ScrollArea className="h-[300px] border rounded-md">
            <div className="p-2">
              {isLoading ? (
                <div className="text-center py-8 text-muted-foreground">
                  Loading directories...
                </div>
              ) : directories.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  No subdirectories found
                </div>
              ) : (
                <div className="space-y-1">
                  {directories.map((dir) => (
                    <button
                      key={dir.path}
                      onClick={() => handleSelectDirectory(dir.path)}
                      className="w-full flex items-center gap-2 px-3 py-2 text-left hover:bg-accent rounded-md transition-colors"
                    >
                      <Folder className="w-4 h-4 text-blue-500 flex-shrink-0" />
                      <span className="flex-1 truncate">{dir.name}</span>
                      <ChevronRight className="w-4 h-4 text-muted-foreground flex-shrink-0" />
                    </button>
                  ))}
                </div>
              )}
            </div>
          </ScrollArea>
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button onClick={handleConfirm} disabled={isLoading}>
            Select This Path
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
