class CodeGenerator:
    def __init__(self, nodes, connections, blocks):
        self.nodes = nodes
        self.connections = connections
        self.blocks = blocks
        self.msgs = []
        self.visited = set()
        self.lang = "c"
        self.goto_targets = {}

    def generate_chain(self, from_id, port, indent):
        conn = next((c for c in self.connections if c["from_node"] == from_id and c["from_port"] == port), None)
        if not conn: return []
        to_node = next((n for n in self.nodes if n.id == conn["to_node"]), None)
        if not to_node or to_node.id in self.visited: return []
        self.visited.add(to_node.id)
        return self.generate_node(to_node, indent)

    def generate_node(self, node, indent):
        block = self.blocks.get(node.type)
        if not block: return []
        lines = block.generate(node, self.lang, indent, self)
        
        if node.id in self.goto_targets and self.lang == "c":
            pad = "    " * indent
            label_line = (f"{pad}{self.goto_targets[node.id]}:", node.id)
            return [label_line] + lines
        return lines

    def generate(self, lang):
        self.lang = lang
        self.visited = set()
        self.msgs = []
        self.goto_targets = {}
        
        if lang == "c":
            for n in self.nodes:
                if n.type == "goto":
                    conn = next((c for c in self.connections if c["from_node"] == n.id and c["from_port"] == "next"), None)
                    if conn:
                        target_id = conn["to_node"]
                        self.goto_targets[target_id] = f"goto_target_{target_id}"
        
        boot = next((n for n in self.nodes if n.type == "boot"), None)
        if not boot:
            body = [("// ERROR: No Boot block", -1)]
        else:
            self.visited.add(boot.id)
            body = self.generate_node(boot, 1)
            
        if lang == "c":
            orphan_targets = []
            for tid in self.goto_targets.keys():
                if tid not in self.visited:
                    t_node = next((n for n in self.nodes if n.id == tid), None)
                    if t_node:
                        orphan_targets.append(t_node)
                        
            if orphan_targets:
                body.append((f"    // --- Orphaned Go To Targets ---", -1))
                for t_node in orphan_targets:
                    self.visited.add(t_node.id)
                    body += self.generate_node(t_node, 1)
        
        triggers = [n for n in self.nodes if n.type == "trigger_cycles" and n.id not in self.visited]
        pre_main = []
        if lang == "c":
            # ALWAYS generate timer_callback so irq0_stub links properly
            pre_main.append("void timer_callback() {")
            if triggers:
                for t in triggers:
                    self.visited.add(t.id)
                    pre_main += [l for l, _ in self.generate_node(t, 1)]
            pre_main.append("}")
            pre_main.append("")
            
            if triggers:
                body.insert(0, ("    __asm__ __volatile__(\"sti\");", -1)) # Enable interrupts
                for t in triggers:
                    freq = t.properties.get("frequency", 10)
                    body.insert(0, (f"    init_timer({freq});", -1))
                body.insert(0, ("    idt_set_gate(0x20, (unsigned long)irq0_stub, 0x08, 0x8E);", -1))
                body.insert(0, ("    init_pic();", -1))
                body.insert(0, ("    init_idt();", -1))
                
            epilogue = C_EPILOGUE.split("\n")
        else:
            epilogue = NASM_EPILOGUE.split("\n")
        
        if lang == "c":
            int_vars = set()
            str_vars = set()
            for n in self.nodes:
                t = n.type
                if t in ["declare_constant", "set_variable", "get_variable"]:
                    int_vars.add(n.properties.get("name", "var"))
                elif t in ["math_add", "math_subtract", "math_multiply", "math_divide", "compare"]:
                    int_vars.add(n.properties.get("result", "res"))
                elif t == "read_keyboard_int":
                    int_vars.add(n.properties.get("var_name", "num"))
                elif t == "read_keyboard_string":
                    str_vars.add(n.properties.get("var_name", "str"))
            
            var_decls = ["    // --- Variable Declarations ---"]
            for v in sorted(int_vars):
                var_decls.append(f"    int {v} = 0;")
            for v in sorted(str_vars):
                var_decls.append(f"    char {v}[64];")
            var_decls.append("")
            
            preamble = C_HEADER.split("\n") + pre_main + C_MAIN_START.split("\n") + var_decls
            all_lines = preamble + [l for l, _ in body] + epilogue
            tags = [None] * len(preamble) + [nid for _, nid in body] + [None] * len(epilogue)
        else:
            preamble = NASM_PREAMBLE.format(msgs="\n".join("    " + m for m in self.msgs)).split("\n")
            all_lines = preamble + [l for l, _ in body] + epilogue
            tags = [None] * len(preamble) + [nid for _, nid in body] + [None] * len(epilogue)
            
        return all_lines, tags

C_HEADER = """// ============================================================
//  kernel.c - Generated by OSDev Visual Scripting
// ============================================================
#include <stdint.h>
volatile uint16_t* vga_buffer = (uint16_t*)0xB8000;
int vga_col = 0;
int vga_row = 0;
#define VGA_COLS 80
#define VGA_ROWS 25

uint8_t current_fg = 0x07;
uint8_t current_bg = 0x00;

// --- Hardware I/O Helpers ---
static inline unsigned char inb(unsigned short port) {
    unsigned char ret;
    __asm__ __volatile__("inb %1, %0" : "=a"(ret) : "d"(port));
    return ret;
}

static inline void outb(unsigned short port, unsigned char val) {
    __asm__ __volatile__("outb %0, %1" : : "a"(val), "Nd"(port));
}

void update_cursor(int row, int col) {
    unsigned short pos = row * VGA_COLS + col;
    outb(0x3D4, 0x0F);
    outb(0x3D5, (unsigned char)(pos & 0xFF));
    outb(0x3D4, 0x0E);
    outb(0x3D5, (unsigned char)((pos >> 8) & 0xFF));
}

void clear_screen(void) {
    uint8_t color = (current_bg << 4) | current_fg;
    for (int i = 0; i < VGA_COLS * VGA_ROWS; i++) {
        vga_buffer[i] = (uint16_t)(color << 8) | ' ';
    }
    vga_col = 0; vga_row = 0;
    update_cursor(vga_row, vga_col);
}

void print_string(const char* str) {
    uint8_t color = (current_bg << 4) | current_fg;
    for (int i = 0; str[i] != '\\0'; i++) {
        if (str[i] == '\\n') {
            vga_col = 0; vga_row++;
            if (vga_row >= VGA_ROWS) vga_row = 0;
            continue;
        }
        vga_buffer[vga_row * VGA_COLS + vga_col] = (uint16_t)(color << 8) | (uint8_t)str[i];
        vga_col++;
        if (vga_col >= VGA_COLS) {
            vga_col = 0; vga_row++;
            if (vga_row >= VGA_ROWS) vga_row = 0;
        }
    }
    update_cursor(vga_row, vga_col);
}

typedef struct { uint32_t magic, flags, checksum; } multiboot_header_t;
__attribute__((section(".multiboot"), used))
multiboot_header_t multiboot_header = { 0x1BADB002, 0x00000000, -(0x1BADB002 + 0x00000000) };

static uint8_t memory_pool[1024 * 1024];
static uint32_t memory_offset = 0;
void* alloc_memory(uint32_t size) {
    void* ptr = &memory_pool[memory_offset];
    memory_offset += size;
    return ptr;
}

// --- IDT and PIC Setup for Background Triggers ---
struct idt_entry {
    unsigned short base_lo;
    unsigned short sel;
    unsigned char always0;
    unsigned char flags;
    unsigned short base_hi;
} __attribute__((packed));

struct idt_ptr {
    unsigned short limit;
    unsigned int base;
} __attribute__((packed));

struct idt_entry idt[256];
struct idt_ptr idtp;

void idt_set_gate(unsigned char num, unsigned long base, unsigned short sel, unsigned char flags) {
    idt[num].base_lo = base & 0xFFFF;
    idt[num].base_hi = (base >> 16) & 0xFFFF;
    idt[num].sel = sel;
    idt[num].always0 = 0;
    idt[num].flags = flags;
}

void init_idt() {
    idtp.limit = sizeof(struct idt_entry) * 256 - 1;
    idtp.base = (unsigned int)&idt;
    __asm__ __volatile__("lidt %0" : : "m"(idtp));
}

void init_pic() {
    outb(0x20, 0x11);
    outb(0xA0, 0x11);
    outb(0x21, 0x20);
    outb(0xA1, 0x28);
    outb(0x21, 0x04);
    outb(0xA1, 0x02);
    outb(0x21, 0x01);
    outb(0xA1, 0x01);
    outb(0x21, 0x00);
    outb(0xA1, 0x00);
}

void init_timer(int frequency) {
    int divisor = 1193180 / frequency;
    outb(0x43, 0x36);
    outb(0x40, (unsigned char)(divisor & 0xFF));
    outb(0x40, (unsigned char)((divisor >> 8) & 0xFF));
}

// Tell C compiler that irq0_stub exists in assembly
extern void irq0_stub(void);

__asm__(
".text\\n"
".global irq0_stub\\n"
"irq0_stub:\\n"
"   push %eax\\n"
"   push %ebx\\n"
"   push %ecx\\n"
"   push %edx\\n"
"   push %esi\\n"
"   push %edi\\n"
"   call timer_callback\\n"
"   mov $0x20, %al\\n"
"   out %al, $0x20\\n"
"   pop %edi\\n"
"   pop %esi\\n"
"   pop %edx\\n"
"   pop %ecx\\n"
"   pop %ebx\\n"
"   pop %eax\\n"
"   iret\\n"
);

typedef void (*isr_handler_t)(void);
static isr_handler_t isr_table[256];
void register_interrupt(uint8_t num, isr_handler_t handler) { isr_table[num] = handler; }
void timer_handler(void) {}
void keyboard_handler(void) {}

unsigned char kbd_us[128] = {
    0,  27, '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', '\\b',
    '\\t', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\\n',
    0, 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\\'', '`',
    0, '\\\\', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 0, '*', 0, ' ',
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
};

void read_string(char* buf) {
    int i = 0;
    while (1) {
        while (!(inb(0x64) & 1));
        unsigned char sc = inb(0x60);
        if (sc & 0x80) continue;
        if (sc == 28) { buf[i] = '\\0'; print_string("\\n"); return; }
        if (sc == 14 && i > 0) {
            i--;
            vga_col--;
            vga_buffer[vga_row * VGA_COLS + vga_col] = (0x07 << 8) | ' ';
            update_cursor(vga_row, vga_col);
            continue;
        }
        char c = kbd_us[sc];
        if (c) {
            buf[i++] = c;
            char str[2] = {c, 0};
            print_string(str);
        }
    }
}

int read_int() {
    char buf[16];
    read_string(buf);
    int val = 0;
    for (int i = 0; buf[i] != '\\0'; i++) {
        if (buf[i] >= '0' && buf[i] <= '9') {
            val = val * 10 + (buf[i] - '0');
        }
    }
    return val;
}

void itoa(int val, char* buf) {
    if (val == 0) { buf[0] = '0'; buf[1] = '\\0'; return; }
    int i = 0, sign = 1;
    if (val < 0) { sign = -1; val = -val; }
    char tmp[16];
    while (val > 0) { tmp[i++] = (val % 10) + '0'; val /= 10; }
    int j = 0;
    if (sign == -1) buf[j++] = '-';
    while (i > 0) buf[j++] = tmp[--i];
    buf[j] = '\\0';
}

void print_int(int val) {
    char buf[16];
    itoa(val, buf);
    print_string(buf);
}
"""

C_MAIN_START = """void kernel_main(void) {
"""

C_EPILOGUE = """
    print_string("\\n\\n== Halting ==\\n");
    while (1) { __asm__ __volatile__("hlt"); }
}
"""

NASM_PREAMBLE = """; ============================================================
;  kernel.asm - Generated by OSDev Visual Scripting
; ============================================================
MB_MAGIC    equ 0x1BADB002
MB_FLAGS    equ 0x00000000
MB_CHECKSUM equ -(MB_MAGIC + MB_FLAGS)

section .multiboot
    dd MB_MAGIC
    dd MB_FLAGS
    dd MB_CHECKSUM

section .bss
    resb 16384
stack_top:
vga_pos: resd 1
current_fg: resb 1
current_bg: resb 1

section .data
{msgs}

section .text
global _start

_start:
    mov esp, stack_top
    mov dword [vga_pos], 0xB8000
    mov byte [current_fg], 0x07
    mov byte [current_bg], 0x00
    call clear_screen
"""

NASM_EPILOGUE = """
    cli
.hang:
    hlt
    jmp .hang

clear_screen:
    pusha
    mov edi, 0xB8000
    mov ecx, 80 * 25
    mov ah, 0x00
    mov al, [current_bg]
    shl al, 4
    or ah, al
    mov al, [current_fg]
    or ah, al
    mov al, ' '
    rep stosw
    mov dword [vga_pos], 0xB8000
    popa
    ret

print_string:
    pusha
    mov edi, [vga_pos]
    mov ah, 0x00
    mov al, [current_bg]
    shl al, 4
    or ah, al
    mov al, [current_fg]
    or ah, al
.loop:
    lodsb
    test al, al
    jz .done
    cmp al, 10
    jne .put_char
    mov eax, edi
    sub eax, 0xB8000
    xor edx, edx
    mov ecx, 160
    div ecx
    inc eax
    mul ecx
    add eax, 0xB8000
    mov edi, eax
    jmp .loop
.put_char:
    mov [edi], ax
    add edi, 2
    jmp .loop
.done:
    mov [vga_pos], edi
    popa
    ret

alloc_memory:
    ret
"""