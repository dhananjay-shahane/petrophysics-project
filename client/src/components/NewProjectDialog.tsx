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
import { useToast } from "@/hooks/use-toast";
import { FolderOpen } from "lucide-react";

interface NewProjectDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export default function NewProjectDialog({ open, onOpenChange }: NewProjectDialogProps) {
  const [projectName, setProjectName] = useState("");
  const [isCreating, setIsCreating] = useState(false);
  const { toast } = useToast();

  const getProjectPath = () => {
    if (projectName.trim()) {
      return `/home/runner/workspace/projects/${projectName.trim()}`;
    }
    return "/home/runner/workspace/projects/[project-name]";
  };

  const handleCreateProject = async () => {
    if (!projectName.trim()) {
      toast({
        title: "Error",
        description: "Please enter a project name",
        variant: "destructive",
      });
      return;
    }

    if (!/^[a-zA-Z0-9_-]+$/.test(projectName.trim())) {
      toast({
        title: "Error",
        description: "Project name can only contain letters, numbers, hyphens, and underscores",
        variant: "destructive",
      });
      return;
    }

    setIsCreating(true);

    try {
      const response = await fetch("/api/projects/create", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: projectName,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to create project");
      }

      const result = await response.json();

      toast({
        title: "Success",
        description: `Project "${projectName}" created successfully in ${result.path}`,
      });

      setProjectName("");
      onOpenChange(false);
    } catch (error: any) {
      const errorMessage = error.message || "Failed to create project. Please try again.";
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
      setProjectName("");
    }
    onOpenChange(open);
  };

  return (
    <Dialog open={open} onOpenChange={handleDialogClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Create New Project</DialogTitle>
          <DialogDescription>
            Enter a project name to create a new project with the standard folder structure.
          </DialogDescription>
        </DialogHeader>
        
        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label htmlFor="project-name">Project Name</Label>
            <Input
              id="project-name"
              placeholder="Enter project name (e.g., MyProject)"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              disabled={isCreating}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !isCreating) {
                  handleCreateProject();
                }
              }}
            />
          </div>

          <div className="grid gap-2">
            <Label htmlFor="project-path">Project Path</Label>
            <div className="flex gap-2 items-center">
              <FolderOpen className="w-4 h-4 text-muted-foreground flex-shrink-0" />
              <Input
                id="project-path"
                value={getProjectPath()}
                readOnly
                disabled={isCreating}
                className="font-mono text-sm"
              />
            </div>
            <p className="text-xs text-muted-foreground">
              This is where your project folders will be created
            </p>
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
          <Button onClick={handleCreateProject} disabled={isCreating}>
            {isCreating ? "Creating..." : "Create Project"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
