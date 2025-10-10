import { useState } from "react";
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
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";

interface NewWellDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  projectPath: string;
  onWellCreated?: (well: { id: string; name: string; path: string }) => void;
}

export default function NewWellDialog({ 
  open, 
  onOpenChange, 
  projectPath,
  onWellCreated 
}: NewWellDialogProps) {
  const [wellName, setWellName] = useState("");
  const [description, setDescription] = useState("");
  const [isCreating, setIsCreating] = useState(false);
  const { toast } = useToast();

  const handleCreateWell = async () => {
    if (!wellName.trim()) {
      toast({
        title: "Error",
        description: "Please enter a well name",
        variant: "destructive",
      });
      return;
    }

    if (!projectPath || projectPath === "No path selected") {
      toast({
        title: "Error",
        description: "No project is currently open. Please open or create a project first.",
        variant: "destructive",
      });
      return;
    }

    if (!/^[a-zA-Z0-9_-]+$/.test(wellName.trim())) {
      toast({
        title: "Error",
        description: "Well name can only contain letters, numbers, hyphens, and underscores",
        variant: "destructive",
      });
      return;
    }

    setIsCreating(true);

    try {
      const response = await fetch("/api/wells/create", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: wellName.trim(),
          projectPath: projectPath,
          description: description.trim() || undefined,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to create well");
      }

      const result = await response.json();

      toast({
        title: "Success",
        description: `Well "${wellName}" created successfully`,
      });

      if (onWellCreated) {
        onWellCreated({
          id: result.well.id,
          name: result.well.name,
          path: result.filePath,
        });
      }

      setWellName("");
      setDescription("");
      onOpenChange(false);
    } catch (error: any) {
      const errorMessage = error.message || "Failed to create well. Please try again.";
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsCreating(false);
    }
  };

  const handleDialogClose = (open: boolean) => {
    if (!open && !isCreating) {
      setWellName("");
      setDescription("");
    }
    onOpenChange(open);
  };

  return (
    <Dialog open={open} onOpenChange={handleDialogClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Create New Well</DialogTitle>
          <DialogDescription>
            Enter well details to create a new well in the current project.
          </DialogDescription>
        </DialogHeader>
        
        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label htmlFor="well-name">Well Name</Label>
            <Input
              id="well-name"
              placeholder="Enter well name (e.g., WELL-001)"
              value={wellName}
              onChange={(e) => setWellName(e.target.value)}
              disabled={isCreating}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !isCreating) {
                  handleCreateWell();
                }
              }}
            />
          </div>

          <div className="grid gap-2">
            <Label htmlFor="well-description">Description (Optional)</Label>
            <Textarea
              id="well-description"
              placeholder="Enter well description or notes..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              disabled={isCreating}
              rows={3}
            />
          </div>

          <div className="text-sm text-muted-foreground">
            <p className="font-medium">Current Project:</p>
            <p className="font-mono text-xs mt-1">{projectPath || "No project selected"}</p>
            {projectPath && projectPath !== "No path selected" && (
              <p className="font-mono text-xs mt-1">
                Will save to: {projectPath}/10-WELLS/{wellName || "[well-name]"}.json
              </p>
            )}
          </div>
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isCreating}
          >
            Cancel
          </Button>
          <Button onClick={handleCreateWell} disabled={isCreating}>
            {isCreating ? "Creating..." : "Create Well"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
