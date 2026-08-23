from pathlib import Path
import plistlib
import struct
import zipfile

out = Path(__file__).parent / "fixtures" / "demo.ipa"
out.parent.mkdir(parents=True, exist_ok=True)
info = {
    "CFBundleIdentifier": "com.etternhall.demoipa",
    "CFBundleDisplayName": "EOS Demo IPA",
    "CFBundleExecutable": "DemoIPA",
    "CFBundleShortVersionString": "0.1",
    "MinimumOSVersion": "17.0",
    "UIDeviceFamily": [1, 2],
}
# Minimal Mach-O 64 header: magic + arm64 CPU type + subtype + file type.
macho = struct.pack("<IIIIIIII", 0xFEEDFACF, 0x0100000C, 0, 2, 0, 0, 0, 0)
with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as archive:
    archive.writestr("Payload/DemoIPA.app/Info.plist", plistlib.dumps(info, fmt=plistlib.FMT_BINARY))
    archive.writestr("Payload/DemoIPA.app/DemoIPA", macho)
print(out)
