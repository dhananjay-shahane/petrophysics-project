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
    <div className="h-8 bg-muted/50 border-b border-border flex items-center px-2 md:px-4 gap-2 md:gap-6 text-xs md:text-sm overflow-x-auto">
      <div className="flex items-center gap-1 md:gap-2 flex-shrink-0">
        <Folder className="w-3 h-3 md:w-4 md:h-4 text-muted-foreground" />
        <span className="text-muted-foreground hidden md:inline">Project:</span>
        <span className="font-medium text-foreground">
          {projectName || "No project"}
        </span>
      </div>
      
      <div className="flex items-center gap-1 md:gap-2 flex-shrink-0 hidden sm:flex">
        <FileText className="w-3 h-3 md:w-4 md:h-4 text-muted-foreground" />
        <span className="text-muted-foreground hidden md:inline">Path:</span>
        <span className="font-mono text-xs text-foreground truncate max-w-[100px] md:max-w-md" title={projectPath}>
          {projectPath || "No path selected"}
        </span>
      </div>
      
      <div className="flex items-center gap-1 md:gap-2 flex-shrink-0">
        <span className="text-muted-foreground">Wells:</span>
        <span className="font-semibold text-foreground">{wellCount}</span>
      </div>
    </div>
  );
}
