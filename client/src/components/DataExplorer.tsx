import { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuTrigger,
} from "@/components/ui/context-menu";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Folder, File, ArrowUp, FolderPlus, Pencil, Trash2, X } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface DataExplorerProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

interface FileItem {
  name: string;
  path: string;
  type: "file" | "directory";
}

interface DataResponse {
  currentPath: string;
  parentPath: string;
  items: FileItem[];
  canGoUp?: boolean;
}

export default function DataExplorer({
  open,
  onOpenChange,
}: DataExplorerProps) {
  const workspaceRoot = "/home/runner/workspace/petrophysics-workplace";
  const [currentPath, setCurrentPath] = useState(workspaceRoot);
  const [parentPath, setParentPath] = useState("");
  const [items, setItems] = useState<FileItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [canGoUp, setCanGoUp] = useState(false);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [newFolderName, setNewFolderName] = useState("");
  const [isCreating, setIsCreating] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [showRenameDialog, setShowRenameDialog] = useState(false);
  const [selectedItem, setSelectedItem] = useState<FileItem | null>(null);
  const [renameItemName, setRenameItemName] = useState("");
  const [isDeleting, setIsDeleting] = useState(false);
  const [isRenaming, setIsRenaming] = useState(false);
  const [selectedFile, setSelectedFile] = useState<FileItem | null>(null);
  const [fileContent, setFileContent] = useState<string>("");
  const { toast } = useToast();

  const loadData = async (path: string) => {
    setIsLoading(true);
    try {
      const response = await fetch(
        `/api/data/list?path=${encodeURIComponent(path)}`,
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to load data");
      }

      const data: DataResponse = await response.json();
      setCurrentPath(data.currentPath);
      setParentPath(data.parentPath);
      setItems(data.items);
      setCanGoUp(data.canGoUp ?? true);
    } catch (error) {
      toast({
        title: "Error",
        description:
          error instanceof Error ? error.message : "Failed to load data",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (open) {
      loadData(workspaceRoot);
      setSelectedFile(null);
      setFileContent("");
    }
  }, [open]);

  const handleSelectItem = async (item: FileItem) => {
    if (item.type === "directory") {
      loadData(item.path);
      setSelectedFile(null);
      setFileContent("");
    } else {
      setSelectedFile(item);
      try {
        const response = await fetch(
          `/api/data/file?path=${encodeURIComponent(item.path)}`,
        );
        if (!response.ok) {
          throw new Error("Failed to read file");
        }
        const data = await response.json();
        setFileContent(JSON.stringify(data.content, null, 2));
      } catch (error) {
        toast({
          title: "Error",
          description: "Failed to read file content",
          variant: "destructive",
        });
      }
    }
  };

  const handleGoUp = () => {
    if (canGoUp && parentPath) {
      loadData(parentPath);
      setSelectedFile(null);
      setFileContent("");
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
      loadData(currentPath);
    } catch (error) {
      toast({
        title: "Error",
        description:
          error instanceof Error ? error.message : "Failed to create folder",
        variant: "destructive",
      });
    } finally {
      setIsCreating(false);
    }
  };

  const handleDeleteItem = async () => {
    if (!selectedItem) return;

    setIsDeleting(true);
    try {
      const response = await fetch("/api/directories/delete", {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          folderPath: selectedItem.path,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to delete item");
      }

      toast({
        title: "Success",
        description: `${selectedItem.type === 'directory' ? 'Folder' : 'File'} deleted successfully`,
      });

      setShowDeleteDialog(false);
      setSelectedItem(null);
      loadData(currentPath);
    } catch (error) {
      toast({
        title: "Error",
        description:
          error instanceof Error ? error.message : "Failed to delete item",
        variant: "destructive",
      });
    } finally {
      setIsDeleting(false);
    }
  };

  const handleRenameItem = async () => {
    if (!selectedItem || !renameItemName.trim()) return;

    setIsRenaming(true);
    try {
      const response = await fetch("/api/directories/rename", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          folderPath: selectedItem.path,
          newName: renameItemName.trim(),
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to rename item");
      }

      toast({
        title: "Success",
        description: `${selectedItem.type === 'directory' ? 'Folder' : 'File'} renamed successfully`,
      });

      setShowRenameDialog(false);
      setSelectedItem(null);
      setRenameItemName("");
      loadData(currentPath);
    } catch (error) {
      toast({
        title: "Error",
        description:
          error instanceof Error ? error.message : "Failed to rename item",
        variant: "destructive",
      });
    } finally {
      setIsRenaming(false);
    }
  };

  const openRenameDialog = (item: FileItem) => {
    setSelectedItem(item);
    setRenameItemName(item.name);
    setShowRenameDialog(true);
  };

  const openDeleteDialog = (item: FileItem) => {
    setSelectedItem(item);
    setShowDeleteDialog(true);
  };

  return (
    <>
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="max-w-6xl h-[600px] flex flex-col">
          <DialogHeader>
            <DialogTitle>Data Explorer</DialogTitle>
            <DialogDescription>
              Browse and manage folders and files in your workspace
            </DialogDescription>
          </DialogHeader>

          <div className="flex-1 flex gap-4 min-h-0">
            <div className="flex-1 flex flex-col min-w-0">
              <div className="flex items-center gap-2 mb-3">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleGoUp}
                  disabled={!canGoUp || isLoading}
                >
                  <ArrowUp className="w-4 h-4 mr-2" />
                  Up
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowCreateDialog(true)}
                  disabled={isLoading}
                >
                  <FolderPlus className="w-4 h-4 mr-2" />
                  New Folder
                </Button>
              </div>

              <div className="text-xs text-muted-foreground mb-2 truncate">
                {currentPath}
              </div>

              <ScrollArea className="flex-1 border rounded-md">
                <div className="p-2">
                  {isLoading ? (
                    <div className="text-center py-8 text-muted-foreground">
                      Loading...
                    </div>
                  ) : items.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                      No items found
                    </div>
                  ) : (
                    items.map((item) => (
                      <ContextMenu key={item.path}>
                        <ContextMenuTrigger>
                          <div
                            className="flex items-center gap-2 p-2 hover:bg-accent rounded cursor-pointer"
                            onClick={() => handleSelectItem(item)}
                          >
                            {item.type === "directory" ? (
                              <Folder className="w-4 h-4 text-blue-500" />
                            ) : (
                              <File className="w-4 h-4 text-gray-500" />
                            )}
                            <span className="text-sm">{item.name}</span>
                          </div>
                        </ContextMenuTrigger>
                        <ContextMenuContent>
                          <ContextMenuItem onClick={() => openRenameDialog(item)}>
                            <Pencil className="w-4 h-4 mr-2" />
                            Rename
                          </ContextMenuItem>
                          <ContextMenuItem 
                            onClick={() => openDeleteDialog(item)}
                            className="text-destructive focus:text-destructive"
                          >
                            <Trash2 className="w-4 h-4 mr-2" />
                            Delete
                          </ContextMenuItem>
                        </ContextMenuContent>
                      </ContextMenu>
                    ))
                  )}
                </div>
              </ScrollArea>
            </div>

            {selectedFile && (
              <div className="flex-1 flex flex-col min-w-0 border-l pl-4">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-sm font-medium truncate">{selectedFile.name}</h3>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      setSelectedFile(null);
                      setFileContent("");
                    }}
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
                <ScrollArea className="flex-1 border rounded-md">
                  <pre className="p-4 text-xs">
                    {fileContent || "No content available"}
                  </pre>
                </ScrollArea>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>

      <AlertDialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Create New Folder</AlertDialogTitle>
            <AlertDialogDescription>
              Enter a name for the new folder
            </AlertDialogDescription>
          </AlertDialogHeader>
          <Input
            value={newFolderName}
            onChange={(e) => setNewFolderName(e.target.value)}
            placeholder="Folder name"
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                handleCreateFolder();
              }
            }}
          />
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleCreateFolder} disabled={isCreating}>
              {isCreating ? "Creating..." : "Create"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <AlertDialog open={showRenameDialog} onOpenChange={setShowRenameDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Rename {selectedItem?.type === 'directory' ? 'Folder' : 'File'}</AlertDialogTitle>
            <AlertDialogDescription>
              Enter a new name for "{selectedItem?.name}"
            </AlertDialogDescription>
          </AlertDialogHeader>
          <Input
            value={renameItemName}
            onChange={(e) => setRenameItemName(e.target.value)}
            placeholder="New name"
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                handleRenameItem();
              }
            }}
          />
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleRenameItem} disabled={isRenaming}>
              {isRenaming ? "Renaming..." : "Rename"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete {selectedItem?.type === 'directory' ? 'Folder' : 'File'}</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete "{selectedItem?.name}"? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteItem}
              disabled={isDeleting}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {isDeleting ? "Deleting..." : "Delete"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
