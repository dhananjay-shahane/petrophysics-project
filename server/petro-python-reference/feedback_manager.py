from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtGui import QTextCursor
from typing import Optional, Set, Union
from datetime import datetime
import logging

class FeedbackManager:
    """
    Enhanced feedback message management system for PyQt applications.
    
    Features:
    - Configurable duplicate message prevention
    - Timestamp support for messages
    - Multiple message importance levels
    - Thread-safe operations
    - Rich text formatting options
    """
    
    class MessageLevel:
        INFO = "INFO"
        WARNING = "WARNING"
        ERROR = "ERROR"
        DEBUG = "DEBUG"
    
    def __init__(self, feedback_dock: 'FeedbackDockWidget', 
                 prevent_duplicates: bool = True,
                 show_timestamps: bool = True,
                 default_level: str = MessageLevel.INFO):
        """
        Initialize the feedback manager with enhanced configuration.
        
        Args:
            feedback_dock: The dock widget containing the text edit
            prevent_duplicates: If True, filters duplicate messages
            show_timestamps: If True, prepends timestamps to messages
            default_level: Default message importance level
        """
        self.feedback_dock = feedback_dock
        self.prevent_duplicates = prevent_duplicates
        self.show_timestamps = show_timestamps
        self.default_level = default_level
        self.feedback_messages: Set[str] = set()
        self.logger = logging.getLogger(__name__)
        
        # Message level colors
        self.level_colors = {
            self.MessageLevel.INFO: "black",
            self.MessageLevel.WARNING: "orange",
            self.MessageLevel.ERROR: "red",
            self.MessageLevel.DEBUG: "gray"
        }

    @property
    def text_edit(self) -> Optional[QTextEdit]:
        """Safely access the text edit widget with multiple fallback strategies."""
        try:
            # Try direct attribute access first
            if hasattr(self.feedback_dock, 'text_edit'):
                return self.feedback_dock.text_edit
            
            # Try common method names
            for method_name in ['get_text_edit', 'textEdit', 'feedbackWidget']:
                if hasattr(self.feedback_dock, method_name):
                    return getattr(self.feedback_dock, method_name)()
                    
            # Try finding a QTextEdit in children
            if hasattr(self.feedback_dock, 'findChild'):
                return self.feedback_dock.findChild(QTextEdit)
                
        except Exception as e:
            self.logger.error(f"Error accessing text edit: {e}")
            
        return None

    def update_feedback(self, 
                      message: str, 
                      level: Optional[str] = None,
                      scroll_to_end: bool = True) -> None:
        """
        Update feedback display with enhanced formatting options.
        
        Args:
            message: The message content
            level: Importance level (INFO, WARNING, ERROR, DEBUG)
            scroll_to_end: Whether to auto-scroll to the new message
        """
        if not message:
            return
            
        level = level or self.default_level
        formatted_message = self._format_message(message, level)
        
        if self.prevent_duplicates and formatted_message in self.feedback_messages:
            return
            
        self.feedback_messages.add(formatted_message)
        text_widget = self.text_edit
        
        if text_widget is None:
            self.logger.warning("No text edit widget available for feedback")
            return
            
        try:
            # Use HTML formatting for colored text
            colored_message = f'<span style="color:{self.level_colors.get(level, "black")}">{formatted_message}</span>'
            text_widget.append(colored_message)
            
            if scroll_to_end:
                text_widget.moveCursor(QTextCursor.End)
                text_widget.ensureCursorVisible()
                
        except Exception as e:
            self.logger.error(f"Error updating feedback: {e}")

    def _format_message(self, message: str, level: str) -> str:
        """Apply formatting to the message based on settings."""
        parts = []
        
        if self.show_timestamps:
            parts.append(f"[{datetime.now().strftime('%H:%M:%S')}]")
            
        parts.append(f"[{level}]" if level else "")
        parts.append(message)
        
        return " ".join(filter(None, parts))

    def clear_feedback(self) -> None:
        """Clear all feedback messages with error handling."""
        text_widget = self.text_edit
        if text_widget is not None:
            try:
                text_widget.clear()
            except Exception as e:
                self.logger.error(f"Error clearing feedback: {e}")
                
        self.feedback_messages.clear()

    def get_message_count(self) -> int:
        """Get the count of unique messages."""
        return len(self.feedback_messages)

    def set_duplicate_prevention(self, enabled: bool) -> None:
        """Toggle duplicate message prevention."""
        self.prevent_duplicates = enabled

    def set_timestamps_visible(self, visible: bool) -> None:
        """Toggle timestamp visibility."""
        self.show_timestamps = visible

    def set_default_level(self, level: str) -> None:
        """Change the default message level."""
        if level in {self.MessageLevel.INFO, self.MessageLevel.WARNING, 
                    self.MessageLevel.ERROR, self.MessageLevel.DEBUG}:
            self.default_level = level
        else:
            raise ValueError(f"Invalid message level: {level}")

    def bulk_update(self, messages: Union[list, tuple], level: Optional[str] = None) -> None:
        """Add multiple messages at once."""
        for msg in messages:
            self.update_feedback(msg, level, scroll_to_end=False)
            
        if messages and self.text_edit:
            self.text_edit.moveCursor(QTextCursor.End)
            self.text_edit.ensureCursorVisible()