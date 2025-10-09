import DockPanel from "./DockPanel";
import { Button } from "@/components/ui/button";
import { Send } from "lucide-react";
import { useState } from "react";

export default function FeedbackPanel({
  onClose,
  onMinimize,
  onMaximize,
}: {
  onClose?: () => void;
  onMinimize?: () => void;
  onMaximize?: () => void;
}) {
  const [message, setMessage] = useState("");

  return (
    <DockPanel
      title="Feedback"
      onClose={onClose}
      onMinimize={onMinimize}
      onMaximize={onMaximize}
    >
      <div className="flex flex-col h-full p-3 gap-3">
        <div className="flex-1">
          <textarea
            className="w-full h-full p-3 text-sm bg-background border border-border rounded resize-none focus:outline-none focus:ring-2 focus:ring-ring"
            placeholder="Drop and drag files here or use the load buttons..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            data-testid="textarea-feedback"
          />
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" data-testid="button-load-log">
            Load Log
          </Button>
          <Button variant="outline" size="sm" data-testid="button-load-csv">
            Load CSV
          </Button>
          <Button
            size="sm"
            className="ml-auto"
            onClick={() => console.log("Send feedback:", message)}
            data-testid="button-send-feedback"
          >
            <Send className="w-3.5 h-3.5 mr-2" />
            Send
          </Button>
        </div>
      </div>
    </DockPanel>
  );
}
