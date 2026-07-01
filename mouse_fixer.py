import sys
import threading
import customtkinter as ctk
import Quartz
from CoreFoundation import CFRunLoopGetCurrent, CFRunLoopAddSource, kCFRunLoopCommonModes, CFRunLoopRun, CFRunLoopStop, kCFAllocatorDefault

class ScrollReverserService:
    def __init__(self, on_permission_error):
        self.on_permission_error = on_permission_error
        self.tap = None
        self.run_loop = None
        self.thread = None
        self.is_running = False

    def event_tap_callback(self, proxy, type_, event, refcon):
        if type_ == Quartz.kCGEventScrollWheel:
            # Check if scroll event is continuous (trackpad / Magic Mouse)
            # is_continuous is 1 for trackpad/Magic Mouse, 0 for standard scroll wheel
            is_continuous = Quartz.CGEventGetIntegerValueField(event, Quartz.kCGScrollWheelEventIsContinuous)
            if not is_continuous:
                # Retrieve standard integer deltas (Axis1: vertical, Axis2: horizontal)
                delta_y = Quartz.CGEventGetIntegerValueField(event, Quartz.kCGScrollWheelEventDeltaAxis1)
                delta_x = Quartz.CGEventGetIntegerValueField(event, Quartz.kCGScrollWheelEventDeltaAxis2)
                
                # Retrieve high-precision fixed point (double) deltas
                fixed_y = Quartz.CGEventGetDoubleValueField(event, Quartz.kCGScrollWheelEventFixedPtDeltaAxis1)
                fixed_x = Quartz.CGEventGetDoubleValueField(event, Quartz.kCGScrollWheelEventFixedPtDeltaAxis2)
                
                # Retrieve point integer deltas
                point_y = Quartz.CGEventGetIntegerValueField(event, Quartz.kCGScrollWheelEventPointDeltaAxis1)
                point_x = Quartz.CGEventGetIntegerValueField(event, Quartz.kCGScrollWheelEventPointDeltaAxis2)
                
                # Negate the deltas to reverse scroll direction
                Quartz.CGEventSetIntegerValueField(event, Quartz.kCGScrollWheelEventDeltaAxis1, -delta_y)
                Quartz.CGEventSetIntegerValueField(event, Quartz.kCGScrollWheelEventDeltaAxis2, -delta_x)
                
                Quartz.CGEventSetDoubleValueField(event, Quartz.kCGScrollWheelEventFixedPtDeltaAxis1, -fixed_y)
                Quartz.CGEventSetDoubleValueField(event, Quartz.kCGScrollWheelEventFixedPtDeltaAxis2, -fixed_x)
                
                Quartz.CGEventSetIntegerValueField(event, Quartz.kCGScrollWheelEventPointDeltaAxis1, -point_y)
                Quartz.CGEventSetIntegerValueField(event, Quartz.kCGScrollWheelEventPointDeltaAxis2, -point_x)
                
        return event

    def _run(self):
        # We hook into physical HID level events (kCGHIDEventTap)
        # Note: kCGHIDEventTap requires Accessibility permission
        self.tap = Quartz.CGEventTapCreate(
            Quartz.kCGHIDEventTap,
            Quartz.kCGHeadInsertEventTap,
            Quartz.kCGEventTapOptionDefault,
            Quartz.CGEventMaskBit(Quartz.kCGEventScrollWheel),
            self.event_tap_callback,
            None
        )
        
        if not self.tap:
            # If event tap creation fails, it's almost certainly due to missing Accessibility permissions
            self.is_running = False
            self.on_permission_error()
            return
            
        run_loop_source = Quartz.CFMachPortCreateRunLoopSource(kCFAllocatorDefault, self.tap, 0)
        self.run_loop = CFRunLoopGetCurrent()
        CFRunLoopAddSource(self.run_loop, run_loop_source, kCFRunLoopCommonModes)
        
        Quartz.CGEventTapEnable(self.tap, True)
        self.is_running = True
        CFRunLoopRun()

    def start(self):
        if self.is_running:
            return True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        return True

    def stop(self):
        if not self.is_running:
            return
        if self.run_loop:
            CFRunLoopStop(self.run_loop)
        self.is_running = False
        self.tap = None
        self.run_loop = None

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window settings
        self.title("Mouse Scroll Fixer")
        self.geometry("460x450")
        self.resizable(False, False)
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        self.service = ScrollReverserService(on_permission_error=self.handle_permission_error)
        
        # Setup modern layout
        self.setup_ui()
        
        # Handle close event cleanly
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_ui(self):
        # Background padding frame
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=30, pady=25)
        
        # Header title
        self.header_label = ctk.CTkLabel(
            self.main_frame,
            text="🐭 Scroll Reverser",
            font=ctk.CTkFont(family="System", size=24, weight="bold")
        )
        self.header_label.pack(pady=(10, 5))
        
        # Subtitle description
        self.sub_label = ctk.CTkLabel(
            self.main_frame,
            text="Oppose external mouse scroll direction to the trackpad",
            font=ctk.CTkFont(family="System", size=13),
            text_color="#9ca3af"
        )
        self.sub_label.pack(pady=(0, 25))
        
        # Service status container frame
        self.status_frame = ctk.CTkFrame(self.main_frame, fg_color="#1f2937", corner_radius=12, height=60)
        self.status_frame.pack(fill="x", pady=(0, 20))
        self.status_frame.pack_propagate(False)
        
        # Status labels
        self.status_title = ctk.CTkLabel(
            self.status_frame,
            text="Service Status:",
            font=ctk.CTkFont(family="System", size=14, weight="normal"),
            text_color="#d1d5db"
        )
        self.status_title.pack(side="left", padx=20)
        
        self.status_value = ctk.CTkLabel(
            self.status_frame,
            text="○ Inactive",
            font=ctk.CTkFont(family="System", size=14, weight="bold"),
            text_color="#9ca3af"
        )
        self.status_value.pack(side="right", padx=20)
        
        # Premium Toggle Switch
        self.toggle_switch = ctk.CTkSwitch(
            self.main_frame,
            text="Enable Scroll Reversal",
            command=self.toggle_service,
            font=ctk.CTkFont(family="System", size=15, weight="normal"),
            progress_color="#10b981", # emerald green when ON
        )
        self.toggle_switch.pack(pady=15)
        
        # Accessibility warning panel (hidden by default)
        self.warning_frame = ctk.CTkFrame(self.main_frame, fg_color="#7f1d1d", corner_radius=8, border_width=1, border_color="#f87171")
        
        self.warning_text = ctk.CTkLabel(
            self.warning_frame,
            text="⚠️ Erişilebilirlik İzni Gerekli\n\nBu uygulamanın çalışabilmesi için fare hareketlerini algılama iznine ihtiyacı var.\n\n1. Aşağıdaki butona tıklayarak Sistem Ayarları'nı açın.\n2. Listede 'Mouse Scroll Fixer' uygulamasını aktif edin.\n3. Uygulamayı yeniden başlatıp anahtarı tekrar açın.",
            font=ctk.CTkFont(family="System", size=11, weight="normal"),
            text_color="#fca5a5",
            justify="left"
        )
        self.warning_text.pack(padx=15, pady=(10, 8))
        
        self.settings_button = ctk.CTkButton(
            self.warning_frame,
            text="🔒 Sistem Ayarlarını Aç",
            command=self.open_accessibility_settings,
            fg_color="#b91c1c",
            hover_color="#991b1b",
            text_color="#ffffff",
            font=ctk.CTkFont(family="System", size=12, weight="normal"),
            height=30
        )
        self.settings_button.pack(padx=15, pady=(0, 10))

    def open_accessibility_settings(self):
        import subprocess
        subprocess.run(["open", "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"])

    def toggle_service(self):
        # Hide warning card if showing
        self.warning_frame.pack_forget()
        
        if self.toggle_switch.get() == 1:
            self.service.start()
            # Wait a fraction of a second to ensure tap wasn't refused
            self.after(100, self.update_status_ui)
        else:
            self.service.stop()
            self.update_status_ui()

    def update_status_ui(self):
        if self.service.is_running:
            self.status_value.configure(text="● Active", text_color="#10b981")
            self.status_frame.configure(fg_color="#064e3b") # dark green highlight
        else:
            self.status_value.configure(text="○ Inactive", text_color="#9ca3af")
            self.status_frame.configure(fg_color="#1f2937")
            self.toggle_switch.deselect()

    def handle_permission_error(self):
        # This will be called from background thread, run UI updates on main thread
        self.after(0, self.show_permission_warning)

    def show_permission_warning(self):
        self.update_status_ui()
        self.warning_frame.pack(fill="x", pady=(15, 0))

    def on_close(self):
        self.service.stop()
        self.destroy()

if __name__ == "__main__":
    app = App()
    
    # Suppress the Python launcher icon from showing in the Dock
    # The AppleScript wrapper app will manage the main Dock icon.
    try:
        import AppKit
        AppKit.NSApplication.sharedApplication().setActivationPolicy_(1) # 1 = NSApplicationActivationPolicyAccessory
    except Exception:
        pass

    app.mainloop()
