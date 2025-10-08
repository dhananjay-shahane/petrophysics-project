import { useRef } from "react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
} from "@/components/ui/dropdown-menu";
import { Check, Sun, Moon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";

interface MenuBarProps {
  onTogglePanel: (panelId: string) => void;
  visiblePanels: Set<string>;
  onSaveLayout: () => void;
  onLoadLayout: () => void;
  theme: "light" | "dark";
  onToggleTheme: () => void;
}

export default function MenuBar({
  onTogglePanel,
  visiblePanels,
  onSaveLayout,
  onLoadLayout,
  theme,
  onToggleTheme,
}: MenuBarProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  const handleNewProject = () => {
    fileInputRef.current?.click();
  };

  const handleFolderSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      const folderPath = files[0].webkitRelativePath.split('/')[0];
      toast({
        title: "Project Opened",
        description: `Selected folder: ${folderPath}`,
      });
    }
  };

  const handleOpen = () => {
    fileInputRef.current?.click();
  };

  const handleSave = () => {
    onSaveLayout();
    toast({
      title: "Project Saved",
      description: "Your project has been saved successfully.",
    });
  };

  const handleImport = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        toast({
          title: "Import Started",
          description: `Importing ${file.name}...`,
        });
      }
    };
    input.click();
  };

  const handleExport = () => {
    const data = { layout: "current", timestamp: new Date().toISOString() };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `project_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    toast({
      title: "Project Exported",
      description: "Your project has been exported successfully.",
    });
  };

  return (
    <>
      <div className="h-10 bg-[#E8F4F5] dark:bg-card border-b border-[#B8D8DC] dark:border-card-border flex items-center justify-between px-2 gap-1">
        <div className="flex items-center gap-1">
          <DropdownMenu>
          <DropdownMenuTrigger className="px-3 py-1 text-sm font-medium text-foreground hover-elevate rounded" data-testid="menu-project">
            Project
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start">
            <DropdownMenuItem onClick={handleNewProject} data-testid="menu-new">New</DropdownMenuItem>
            <DropdownMenuItem onClick={handleOpen} data-testid="menu-open">Open</DropdownMenuItem>
            <DropdownMenuItem onClick={handleSave} data-testid="menu-save">Save</DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={() => onTogglePanel("dataBrowser")} data-testid="menu-new-dockable">New Dockable Window</DropdownMenuItem>
            <DropdownMenuItem data-testid="menu-remove-widget">Remove Central Widget</DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem data-testid="menu-exit">Exit</DropdownMenuItem>
          </DropdownMenuContent>
          </DropdownMenu>

          <DropdownMenu>
            <DropdownMenuTrigger className="px-3 py-1 text-sm font-medium text-foreground hover-elevate rounded" data-testid="menu-file">
              File
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start">
              <DropdownMenuItem onClick={handleImport} data-testid="menu-import">Import</DropdownMenuItem>
              <DropdownMenuItem onClick={handleExport} data-testid="menu-export">Export</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          <DropdownMenu>
            <DropdownMenuTrigger className="px-3 py-1 text-sm font-medium text-foreground hover-elevate rounded" data-testid="menu-petrophysics">
              Petrophysics
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start">
              <DropdownMenuItem onClick={() => toast({ title: "Analysis Tools", description: "Opening analysis tools..." })} data-testid="menu-analysis">Analysis Tools</DropdownMenuItem>
              <DropdownMenuItem onClick={() => toast({ title: "Calculations", description: "Opening calculations..." })} data-testid="menu-calculations">Calculations</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          <DropdownMenu>
            <DropdownMenuTrigger className="px-3 py-1 text-sm font-medium text-foreground hover-elevate rounded" data-testid="menu-geolog">
              Geolog
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start">
              <DropdownMenuItem onClick={() => toast({ title: "Geolog Utilities", description: "Opening Geolog utilities..." })} data-testid="menu-geolog-utilities">Open Geolog Utilities</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          <DropdownMenu>
            <DropdownMenuTrigger className="px-3 py-1 text-sm font-medium text-foreground hover-elevate rounded" data-testid="menu-dock">
              Dock
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start">
              <DropdownMenuItem onClick={() => onTogglePanel("wells")} data-testid="menu-toggle-wells">
                {visiblePanels.has("wells") && <Check className="w-4 h-4 mr-2" />}
                {!visiblePanels.has("wells") && <span className="w-4 mr-2" />}
                Toggle Wells
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => onTogglePanel("zonation")} data-testid="menu-toggle-zonation">
                {visiblePanels.has("zonation") && <Check className="w-4 h-4 mr-2" />}
                {!visiblePanels.has("zonation") && <span className="w-4 mr-2" />}
                Toggle Tops
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => onTogglePanel("dataBrowser")} data-testid="menu-toggle-databrowser">
                {visiblePanels.has("dataBrowser") && <Check className="w-4 h-4 mr-2" />}
                {!visiblePanels.has("dataBrowser") && <span className="w-4 mr-2" />}
                Toggle DatasetBrowser
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => onTogglePanel("feedback")} data-testid="menu-toggle-feedback">
                {visiblePanels.has("feedback") && <Check className="w-4 h-4 mr-2" />}
                {!visiblePanels.has("feedback") && <span className="w-4 mr-2" />}
                Toggle Feedback
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={onSaveLayout} data-testid="menu-save-layout">
                Save Layout
              </DropdownMenuItem>
              <DropdownMenuItem onClick={onLoadLayout} data-testid="menu-load-layout">
                Load Layout
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={onToggleTheme} data-testid="menu-toggle-theme">
                Toggle Theme
              </DropdownMenuItem>
              <DropdownMenuSub>
                <DropdownMenuSubTrigger data-testid="menu-select-theme">Select Theme</DropdownMenuSubTrigger>
                <DropdownMenuSubContent>
                  <DropdownMenuItem onClick={() => theme !== "light" && onToggleTheme()} data-testid="menu-theme-light">
                    {theme === "light" && <Check className="w-4 h-4 mr-2" />}
                    {theme !== "light" && <span className="w-4 mr-2" />}
                    Light
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => theme !== "dark" && onToggleTheme()} data-testid="menu-theme-dark">
                    {theme === "dark" && <Check className="w-4 h-4 mr-2" />}
                    {theme !== "dark" && <span className="w-4 mr-2" />}
                    Dark
                  </DropdownMenuItem>
                </DropdownMenuSubContent>
              </DropdownMenuSub>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
        
        <Button
          variant="ghost"
          size="icon"
          onClick={onToggleTheme}
          className="h-8 w-8"
          data-testid="button-toggle-theme"
        >
          {theme === "light" ? (
            <Moon className="h-4 w-4" />
          ) : (
            <Sun className="h-4 w-4" />
          )}
        </Button>
      </div>
      
      <input
        ref={fileInputRef}
        type="file"
        className="hidden"
        {...({ webkitdirectory: "", directory: "" } as any)}
        multiple
        onChange={handleFolderSelect}
      />
    </>
  );
}
