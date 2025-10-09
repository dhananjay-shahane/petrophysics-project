import { Folder, FileText } from "lucide-react";

interface ProjectInfoBarProps {
  projectPath: string;
  projectName: string;
  wellCount: number;
}

export default function ProjectInfoBar({
  projectPath,
  projectName,
  wellCount,
}: ProjectInfoBarProps) {
  return (
    <div className="h-8 bg-muted/50 border-b border-border flex items-center px-4 gap-6 text-sm">
      <div className="flex items-center gap-2">
        <Folder className="w-4 h-4 text-muted-foreground" />
        <span className="text-muted-foreground">Project:</span>
        <span className="font-medium text-foreground">
          {projectName || "No project"}
        </span>
      </div>
      
      <div className="flex items-center gap-2">
        <FileText className="w-4 h-4 text-muted-foreground" />
        <span className="text-muted-foreground">Path:</span>
        <span className="font-mono text-xs text-foreground truncate max-w-md" title={projectPath}>
          {projectPath || "No path selected"}
        </span>
      </div>
      
      <div className="flex items-center gap-2">
        <span className="text-muted-foreground">Wells:</span>
        <span className="font-semibold text-foreground">{wellCount}</span>
      </div>
    </div>
  );
}
