import subprocess
import os
import tempfile
import threading

class Runner:
    def __init__(self, status_var):
        self.status_var = status_var

    def run(self, code, lang):
        threading.Thread(target=self._worker, args=(code, lang), daemon=True).start()

    def _worker(self, code, lang):
        tmpdir = tempfile.mkdtemp()
        if lang == "c":
            src = os.path.join(tmpdir, "kernel.c")
            with open(src, "w") as f: f.write(code)
            ld = os.path.join(tmpdir, "linker.ld")
            with open(ld, "w") as f: f.write(LINKER_LD)
            
            self.status_var.set("Compiling C...")
            res = subprocess.run(["gcc", "-m32", "-ffreestanding", "-fno-pie", "-nostdlib", "-fno-stack-protector", "-c", src, "-o", os.path.join(tmpdir, "kernel.o")], capture_output=True, text=True)
            if res.returncode != 0:
                self.status_var.set(f"Compile Error:\n{res.stderr}")
                return
                
            self.status_var.set("Linking...")
            res = subprocess.run(["ld", "-m", "elf_i386", "-T", ld, "-z", "noexecstack", "--no-warn-rwx-segments", "-o", os.path.join(tmpdir, "kernel.bin"), os.path.join(tmpdir, "kernel.o")], capture_output=True, text=True)
            if res.returncode != 0:
                self.status_var.set(f"Link Error:\n{res.stderr}")
                return
        else:
            src = os.path.join(tmpdir, "kernel.asm")
            with open(src, "w") as f: f.write(code)
            ld = os.path.join(tmpdir, "linker.ld")
            with open(ld, "w") as f: f.write(LINKER_LD)
            
            self.status_var.set("Assembling NASM...")
            res = subprocess.run(["nasm", "-f", "elf32", src, "-o", os.path.join(tmpdir, "kernel.o")], capture_output=True, text=True)
            if res.returncode != 0:
                self.status_var.set(f"Assemble Error:\n{res.stderr}")
                return
                
            self.status_var.set("Linking...")
            res = subprocess.run(["ld", "-m", "elf_i386", "-T", ld, "-z", "noexecstack", "--no-warn-rwx-segments", "-o", os.path.join(tmpdir, "kernel.bin"), os.path.join(tmpdir, "kernel.o")], capture_output=True, text=True)
            if res.returncode != 0:
                self.status_var.set(f"Link Error:\n{res.stderr}")
                return

        self.status_var.set("Launching QEMU...")
        bin_path = os.path.join(tmpdir, "kernel.bin")
        try:
            subprocess.run(["qemu-system-i386", "-kernel", bin_path, "-display", "gtk"], check=True)
            self.status_var.set("Done. QEMU closed.")
        except FileNotFoundError:
            self.status_var.set("Error: qemu-system-i386 not found. Please install QEMU.")
        except subprocess.CalledProcessError as e:
            self.status_var.set(f"QEMU Error:\n{e.stderr}")

LINKER_LD = """ENTRY(kernel_main)
SECTIONS {
    . = 1M;
    .multiboot : { *(.multiboot) }
    .text      : { *(.text) }
    .data      : { *(.data) }
    .rodata    : { *(.rodata) }
    .bss       : { *(.bss) }
}
"""