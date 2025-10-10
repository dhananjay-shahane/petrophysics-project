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
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Folder, ArrowUp, FolderPlus } from "lucide-react";
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
  canGoUp?: boolean;
}

export default function DirectoryPicker({
  open,
  onOpenChange,
  onSelectPath,
  initialPath,
}: DirectoryPickerProps) {
  const workspaceRoot = "/home/runner/workspace/petrophysics-workplace";
  const [currentPath, setCurrentPath] = useState(initialPath || workspaceRoot);
  const [parentPath, setParentPath] = useState("");
  const [directories, setDirectories] = useState<Directory[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [canGoUp, setCanGoUp] = useState(false);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [newFolderName, setNewFolderName] = useState("");
  const [isCreating, setIsCreating] = useState(false);
  const { toast } = useToast();

  const loadDirectories = async (path: string) => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/directories/list?path=${encodeURIComponent(path)}`);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to load directories");
      }

      const data: DirectoryResponse = await response.json();
      setCurrentPath(data.currentPath);
      setParentPath(data.parentPath);
      setDirectories(data.directories);
      setCanGoUp(data.canGoUp ?? true);
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to load directories",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (open) {
      const pathToLoad = initialPath || workspaceRoot;
      loadDirectories(pathToLoad);
    }
  }, [open]);

  const handleSelectDirectory = (dirPath: string) => {
    loadDirectories(dirPath);
  };

  const handleGoUp = () => {
    if (canGoUp && parentPath) {
      loadDirectories(parentPath);
    }
  };

  const handleCreateFolder = async () => {
    if (!newFolderName.trim()) {
      toast({
        title: "Error",
        description: "Please enter a folder name",
        variant: "destructive",
      });
      return;
    }

    setIsCreating(true);
    try {
      const response = await fetch("/api/directories/create", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          parentPath: currentPath,
          folderName: newFolderName.trim(),
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to create folder");
      }

      toast({
        title: "Success",
        description: "Folder created successfully",
      });

      setNewFolderName("");
      setShowCreateDialog(false);
      loadDirectories(currentPath);
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to create folder",
        variant: "destructive",
      });
    } finally {
      setIsCreating(false);
    }
  };

  const handleConfirm = () => {
    onSelectPath(currentPath);
    onOpenChange(false);
  };

  return (
    <>
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="sm:max-w-[700px]">
          <DialogHeader>
            <DialogTitle>Choose Directory Path</DialogTitle>
            <DialogDescription>
              Browse petrophysics-workplace and select where to create your project
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleGoUp}
                disabled={isLoading || !canGoUp}
                title="Go up one level"
              >
                <ArrowUp className="w-4 h-4" />
              </Button>
              <div className="flex-1 px-3 py-2 bg-muted rounded-md font-mono text-sm truncate">
                {currentPath.replace('/home/runner/workspace/', '')}
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowCreateDialog(true)}
                disabled={isLoading}
                title="Create new folder"
              >
                <FolderPlus className="w-4 h-4 mr-2" />
                New Folder
              </Button>
            </div>

            <ScrollArea className="h-[350px] border rounded-md">
              <div className="p-4">
                {isLoading ? (
                  <div className="text-center py-12 text-muted-foreground">
                    Loading directories...
                  </div>
                ) : directories.length === 0 ? (
                  <div className="text-center py-12 text-muted-foreground">
                    <Folder className="w-12 h-12 mx-auto mb-3 opacity-50" />
                    <p>No folders found</p>
                    <p className="text-sm mt-1">Create a new folder to get started</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-3 gap-3">
                    {directories.map((dir) => (
                      <button
                        key={dir.path}
                        onClick={() => handleSelectDirectory(dir.path)}
                        className="flex flex-col items-center gap-2 p-4 text-center hover:bg-accent rounded-lg transition-colors border border-transparent hover:border-primary/20"
                      >
                        <Folder className="w-12 h-12 text-blue-500" />
                        <span className="text-sm font-medium truncate w-full" title={dir.name}>
                          {dir.name}
                        </span>
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

      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Create New Folder</DialogTitle>
            <DialogDescription>
              Enter a name for the new folder (letters, numbers, hyphens, and underscores only)
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <Input
              placeholder="Folder name"
              value={newFolderName}
              onChange={(e) => setNewFolderName(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !isCreating) {
                  handleCreateFolder();
                }
              }}
              disabled={isCreating}
            />
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setShowCreateDialog(false);
                setNewFolderName("");
              }}
              disabled={isCreating}
            >
              Cancel
            </Button>
            <Button onClick={handleCreateFolder} disabled={isCreating}>
              {isCreating ? "Creating..." : "Create Folder"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
