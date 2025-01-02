import customtkinter as ctk


class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.delay = 500
        self.bg_color = "#444648"
        self.text_color = "#AEAEAE"
        self.font = ("Roboto", 12)
        self.tooltip_window = None
        self.after_id = None

        # Bind events
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<Motion>", self.on_motion)

    def on_enter(self, event=None):
        self.after_id = self.widget.after(self.delay, self.show_tooltip(event))

    def on_leave(self, event=None):
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None
        self.hide_tooltip()

    def on_motion(self, event=None):
        if self.tooltip_window:
            x = self.widget.winfo_rootx() + event.x + 20
            y = self.widget.winfo_rooty() + event.y - 40
            self.tooltip_window.geometry(f"+{x}+{y}")

    def show_tooltip(self, event):
        if self.tooltip_window or not self.text:
            return

        x = event.x_root + 20
        y = event.y_root - 40

        # Create tooltip window
        self.tooltip_window = ctk.CTkToplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)  # Remove window decorations
        self.tooltip_window.geometry(f"+{x}+{y}")
        self.tooltip_window.configure(bg_color=self.bg_color)

        # Add a label to the tooltip window
        label = ctk.CTkLabel(
            self.tooltip_window,
            text=self.text,
            text_color=self.text_color,
            font=self.font,
            corner_radius=2,
            fg_color=self.bg_color
        )
        label.pack()

    def hide_tooltip(self):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
