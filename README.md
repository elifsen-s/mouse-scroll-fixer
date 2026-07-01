# Mouse Scroll Fixer 🐭

Mouse Scroll Fixer is a lightweight, native macOS desktop utility that resolves the scrolling conflict between external mice and trackpads. It allows you to reverse the scroll direction of your external Bluetooth/USB mouse wheel while keeping your trackpad's scroll direction natural.

Written natively in **Swift (Cocoa)** for optimal performance, system integration, and security.

## Features

- **Opposite Scroll Direction**: Reverses external mouse wheel scroll direction while preserving natural trackpad scrolling.
- **Dock Integration**: Minimizes and restores natively from the Dock.
- **Compact & Fast**: Compiled as a native 150 KB Apple binary with zero dependencies.
- **Cmd + Q Support**: Close the application natively using standard shortcuts.

---

## How to Install (Using pre-compiled Release)

1. Go to the **Releases** section on the right sidebar of this repository.
2. Download the `Mouse.Scroll.Fixer.zip` archive.
3. Unzip the file and move **Mouse Scroll Fixer.app** to your `/Applications` folder or your **Desktop**.
4. Double-click to open it!

> 💡 **Gatekeeper Warning**: 
> If macOS says the app is "damaged" or "cannot be opened because it is from an unidentified developer", open your Terminal and run the following command to unlock it:
> ```bash
> xattr -r -d com.apple.quarantine "/Applications/Mouse Scroll Fixer.app"
> ```
> (Replace the path if you saved it on your Desktop).

---

## How to Compile from Source (For Developers)

Since macOS includes the Swift compiler (`swiftc`) natively, you can compile and package the app yourself in seconds:

1. Clone this repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/mouse-scroll-fixer.git
   cd mouse-scroll-fixer
   ```
2. Compile and package the app:
   ```bash
   swiftc -O -sdk $(xcrun --show-sdk-path) main.swift -o "Mouse Scroll Fixer" && \
   mkdir -p "Mouse Scroll Fixer.app/Contents/MacOS" && \
   mkdir -p "Mouse Scroll Fixer.app/Contents/Resources" && \
   mv "Mouse Scroll Fixer" "Mouse Scroll Fixer.app/Contents/MacOS/" && \
   cp "Info.plist" "Mouse Scroll Fixer.app/Contents/Info.plist" && \
   cp "AppIcon.icns" "Mouse Scroll Fixer.app/Contents/Resources/AppIcon.icns"
   ```
3. Drag **Mouse Scroll Fixer.app** to your Desktop or Applications folder.

---

## Permissions

This utility requires **Accessibility (Erişilebilirlik)** permissions in macOS to intercept mouse wheel events.
- On first launch, the app will show a **"⚠️ İzin Bekleniyor..."** status.
- Click **"🔒 Sistem Ayarlarını Aç"** to open settings.
- Find **Mouse Scroll Fixer** in the list and toggle the switch to **ON**.
- **Restart** the application to apply the permissions.
