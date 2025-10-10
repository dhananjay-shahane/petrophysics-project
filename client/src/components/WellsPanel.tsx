import DockPanel from "./DockPanel";
import TreeView from "./TreeView";

export default function WellsPanel({ onClose }: { onClose?: () => void }) {
  const wellsData = [
    {
      id: "view-all",
      label: "View All",
      type: "folder" as const,
    },
    {
      id: "0-to-100m",
      label: "0 to 100m",
      type: "folder" as const,
    },
    {
      id: "derivative-zone-1",
      label: "Derivative Zone 1",
      type: "folder" as const,
    },
  ];

  return (
    <DockPanel title="Wells" onClose={onClose}>
      <div className="p-2">
        <TreeView data={wellsData} />
      </div>
    </DockPanel>
  );
}
