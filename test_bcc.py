from bcc import BPF

prog = r"""
int kprobe__sys_clone(void *ctx) {
    bpf_trace_printk("hello from eBPF\\n");
    return 0;
}
"""

b = BPF(text=prog)
print("Loaded BPF program. Now check /sys/kernel/debug/tracing/trace_pipe ...")
b.trace_print()
