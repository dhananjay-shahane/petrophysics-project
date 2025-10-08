import { useState } from "react";
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
import { Check } from "lucide-react";

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
  return (
    <div className="h-10 bg-[#E8F4F5] dark:bg-card border-b border-[#B8D8DC] dark:border-card-border flex items-center px-2 gap-1">
      <DropdownMenu>
        <DropdownMenuTrigger className="px-3 py-1 text-sm font-medium text-foreground hover-elevate rounded" data-testid="menu-project">
          Project
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start">
          <DropdownMenuItem data-testid="menu-new">New</DropdownMenuItem>
          <DropdownMenuItem data-testid="menu-open">Open</DropdownMenuItem>
          <DropdownMenuItem data-testid="menu-save">Save</DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem data-testid="menu-new-dockable">New Dockable Window</DropdownMenuItem>
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
          <DropdownMenuItem data-testid="menu-import">Import</DropdownMenuItem>
          <DropdownMenuItem data-testid="menu-export">Export</DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      <DropdownMenu>
        <DropdownMenuTrigger className="px-3 py-1 text-sm font-medium text-foreground hover-elevate rounded" data-testid="menu-petrophysics">
          Petrophysics
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start">
          <DropdownMenuItem data-testid="menu-analysis">Analysis Tools</DropdownMenuItem>
          <DropdownMenuItem data-testid="menu-calculations">Calculations</DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      <DropdownMenu>
        <DropdownMenuTrigger className="px-3 py-1 text-sm font-medium text-foreground hover-elevate rounded" data-testid="menu-geolog">
          Geolog
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start">
          <DropdownMenuItem data-testid="menu-geolog-utilities">Open Geolog Utilities</DropdownMenuItem>
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
              <DropdownMenuItem data-testid="menu-theme-light">
                {theme === "light" && <Check className="w-4 h-4 mr-2" />}
                {theme !== "light" && <span className="w-4 mr-2" />}
                Light
              </DropdownMenuItem>
              <DropdownMenuItem data-testid="menu-theme-dark">
                {theme === "dark" && <Check className="w-4 h-4 mr-2" />}
                {theme !== "dark" && <span className="w-4 mr-2" />}
                Dark
              </DropdownMenuItem>
            </DropdownMenuSubContent>
          </DropdownMenuSub>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}
