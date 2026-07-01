import Cocoa
import CoreGraphics
import ApplicationServices

class AppDelegate: NSObject, NSApplicationDelegate {
    var window: NSWindow!
    var statusLabel: NSTextField!
    var toggleSwitch: NSSwitch!
    var warningLabel: NSTextField!
    var settingsButton: NSButton!
    
    var eventTap: CFMachPort?
    var runLoopSource: CFRunLoopSource?
    var isServiceActive = false

    func applicationDidFinishLaunching(_ notification: Notification) {
        // Create standard macOS application menu bar (enables Cmd+Q quit shortcut)
        setupMenuBar()

        // Create window
        let windowRect = NSRect(x: 0, y: 0, width: 440, height: 350)
        window = NSWindow(
            contentRect: windowRect,
            styleMask: [.titled, .closable, .miniaturizable],
            backing: .buffered,
            defer: false
        )
        window.title = "Mouse Scroll Fixer"
        window.center()
        window.makeKeyAndOrderFront(nil)
        
        // Hide standard window zoom, keep minimize and close
        window.standardWindowButton(.zoomButton)?.isHidden = true
        
        // Set Dark Background
        window.backgroundColor = NSColor.windowBackgroundColor
        
        // Setup UI
        let contentView = window.contentView!
        
        // Title Label
        let titleLabel = NSTextField(labelWithString: "🐭 Scroll Reverser")
        titleLabel.font = NSFont.boldSystemFont(ofSize: 22)
        titleLabel.textColor = .labelColor
        titleLabel.frame = NSRect(x: 20, y: 280, width: 400, height: 30)
        titleLabel.alignment = .center
        contentView.addSubview(titleLabel)
        
        // Subtitle Label
        let subtitleLabel = NSTextField(labelWithString: "Fare kaydırma yönünü trackpad ile tersler")
        subtitleLabel.font = NSFont.systemFont(ofSize: 12)
        subtitleLabel.textColor = .secondaryLabelColor
        subtitleLabel.frame = NSRect(x: 20, y: 255, width: 400, height: 20)
        subtitleLabel.alignment = .center
        contentView.addSubview(subtitleLabel)
        
        // Status Container Box
        let statusBox = NSBox()
        statusBox.frame = NSRect(x: 40, y: 170, width: 360, height: 65)
        statusBox.boxType = .custom
        statusBox.cornerRadius = 10
        statusBox.borderWidth = 1
        statusBox.borderColor = NSColor.separatorColor
        statusBox.fillColor = NSColor.controlBackgroundColor
        contentView.addSubview(statusBox)
        
        // Status Label Inside Box
        statusLabel = NSTextField(labelWithString: "○ Servis Durumu: İnaktif")
        statusLabel.font = NSFont.boldSystemFont(ofSize: 14)
        statusLabel.textColor = .secondaryLabelColor
        statusLabel.frame = NSRect(x: 10, y: 22, width: 340, height: 20)
        statusLabel.alignment = .center
        statusBox.addSubview(statusLabel)
        
        // Toggle Switch Label
        let switchLabel = NSTextField(labelWithString: "Ters Kaydırmayı Aktif Et:")
        switchLabel.font = NSFont.systemFont(ofSize: 14, weight: .medium)
        switchLabel.textColor = .labelColor
        switchLabel.frame = NSRect(x: 80, y: 110, width: 200, height: 25)
        switchLabel.alignment = .left
        contentView.addSubview(switchLabel)
        
        // Toggle Switch
        toggleSwitch = NSSwitch()
        toggleSwitch.frame = NSRect(x: 290, y: 110, width: 60, height: 30)
        toggleSwitch.target = self
        toggleSwitch.action = #selector(toggleSwitchChanged)
        contentView.addSubview(toggleSwitch)
        
        // Warning Label (Hidden by default)
        warningLabel = NSTextField(labelWithString: "⚠️ Sistem Ayarları'ndan izni açın ve ardından\nuygulamayı kapatıp yeniden başlatın.")
        warningLabel.font = NSFont.systemFont(ofSize: 12, weight: .medium)
        warningLabel.textColor = .systemRed
        warningLabel.alignment = .center
        warningLabel.frame = NSRect(x: 20, y: 55, width: 400, height: 35)
        warningLabel.isHidden = true
        contentView.addSubview(warningLabel)
        
        // Open Settings Button (Hidden by default)
        settingsButton = NSButton(title: "🔒 Sistem Ayarlarını Aç", target: self, action: #selector(openSettingsClicked))
        settingsButton.frame = NSRect(x: 130, y: 20, width: 180, height: 28)
        settingsButton.bezelStyle = .rounded
        settingsButton.isHidden = true
        contentView.addSubview(settingsButton)
        
        // Check if permission is already granted on launch
        checkCurrentPermission()
    }
    
    func setupMenuBar() {
        let mainMenu = NSMenu()
        let appMenuItem = NSMenuItem()
        mainMenu.addItem(appMenuItem)
        
        let appMenu = NSMenu()
        let quitMenuItem = NSMenuItem(
            title: "Quit Mouse Scroll Fixer",
            action: #selector(NSApplication.terminate(_:)),
            keyEquivalent: "q"
        )
        appMenu.addItem(quitMenuItem)
        appMenuItem.submenu = appMenu
        NSApplication.shared.mainMenu = mainMenu
    }
    
    func checkCurrentPermission() {
        // Quick permission check without displaying settings
        let options = [kAXTrustedCheckOptionPrompt.takeUnretainedValue() as String: false] as CFDictionary
        let access = AXIsProcessTrustedWithOptions(options)
        if access {
            toggleSwitch.state = .on
            startService()
        }
    }
    
    @objc func toggleSwitchChanged() {
        warningLabel.isHidden = true
        settingsButton.isHidden = true
        
        if toggleSwitch.state == .on {
            startService()
        } else {
            stopService()
        }
    }
    
    @objc func openSettingsClicked() {
        if let url = URL(string: "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility") {
            NSWorkspace.shared.open(url)
        }
    }
    
    func startService() {
        let mask = CGEventMask(1 << CGEventType.scrollWheel.rawValue)
        
        // Create event tap callback
        let callback: CGEventTapCallBack = { (proxy, type, event, refcon) -> Unmanaged<CGEvent>? in
            if type == .scrollWheel {
                let isContinuous = event.getIntegerValueField(.scrollWheelEventIsContinuous)
                if isContinuous == 0 {
                    let deltaY = event.getIntegerValueField(.scrollWheelEventDeltaAxis1)
                    let deltaX = event.getIntegerValueField(.scrollWheelEventDeltaAxis2)
                    let fixedY = event.getDoubleValueField(.scrollWheelEventFixedPtDeltaAxis1)
                    let fixedX = event.getDoubleValueField(.scrollWheelEventFixedPtDeltaAxis2)
                    let pointY = event.getIntegerValueField(.scrollWheelEventPointDeltaAxis1)
                    let pointX = event.getIntegerValueField(.scrollWheelEventPointDeltaAxis2)
                    
                    event.setIntegerValueField(.scrollWheelEventDeltaAxis1, value: -deltaY)
                    event.setIntegerValueField(.scrollWheelEventDeltaAxis2, value: -deltaX)
                    event.setDoubleValueField(.scrollWheelEventFixedPtDeltaAxis1, value: -fixedY)
                    event.setDoubleValueField(.scrollWheelEventFixedPtDeltaAxis2, value: -fixedX)
                    event.setIntegerValueField(.scrollWheelEventPointDeltaAxis1, value: -pointY)
                    event.setIntegerValueField(.scrollWheelEventPointDeltaAxis2, value: -pointX)
                }
            }
            return Unmanaged.passRetained(event)
        }
        
        eventTap = CGEvent.tapCreate(
            tap: .cgSessionEventTap,
            place: .headInsertEventTap,
            options: .defaultTap,
            eventsOfInterest: mask,
            callback: callback,
            userInfo: nil
        )
        
        if eventTap == nil {
            // Permission missing
            toggleSwitch.state = .off
            warningLabel.isHidden = false
            settingsButton.isHidden = false
            statusLabel.stringValue = "⚠️ İzin Bekleniyor..."
            statusLabel.textColor = .systemRed
            return
        }
        
        runLoopSource = CFMachPortCreateRunLoopSource(kCFAllocatorDefault, eventTap!, 0)
        CFRunLoopAddSource(CFRunLoopGetCurrent(), runLoopSource, .commonModes)
        CGEvent.tapEnable(tap: eventTap!, enable: true)
        
        isServiceActive = true
        statusLabel.stringValue = "● Servis Aktif"
        statusLabel.textColor = .systemGreen
    }
    
    func stopService() {
        if isServiceActive {
            if let tap = eventTap {
                CGEvent.tapEnable(tap: tap, enable: false)
            }
            if let source = runLoopSource {
                CFRunLoopRemoveSource(CFRunLoopGetCurrent(), source, .commonModes)
            }
            eventTap = nil
            runLoopSource = nil
            isServiceActive = false
        }
        statusLabel.stringValue = "○ Servis Durumu: İnaktif"
        statusLabel.textColor = .secondaryLabelColor
    }
    
    func applicationWillTerminate(_ notification: Notification) {
        stopService()
    }
}

// Main execution
let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.run()
