#!/usr/bin/env python3
import asyncio, json, sys, threading, tkinter as tk
from tkinter import ttk

class VibeWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('VibeScreen')
        self.root.geometry('450x350')
        self.frame = ttk.Frame(self.root, padding=20)
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.result = None
        self.inputs = {}

    def render(self, schema):
        for w in self.frame.winfo_children(): w.destroy()
        self.result = None
        self.inputs = {}
        if schema.get('title'):
            ttk.Label(self.frame, text=schema['title'], font=('TkDefaultFont', 12, 'bold')).pack(pady=(0, 5))
        if schema.get('description'):
            ttk.Label(self.frame, text=schema['description'], wraplength=400).pack(pady=(0, 15))
        for field in schema.get('fields', []):
            name, label, ftype = field['name'], field.get('label', field['name'].replace('_', ' ').title()), field.get('type', 'text')
            ttk.Label(self.frame, text=label + (' *' if field.get('required') else '')).pack(anchor=tk.W, pady=(10, 2))
            if ftype == 'select':
                var = tk.StringVar(value=field.get('default', field.get('options', [''])[0]))
                w = ttk.Combobox(self.frame, textvariable=var, values=field.get('options', []), state='readonly')
                w.pack(fill=tk.X); self.inputs[name] = var
            elif ftype == 'checkbox':
                var = tk.BooleanVar(value=field.get('default', False))
                w = ttk.Checkbutton(self.frame, variable=var); w.pack(anchor=tk.W); self.inputs[name] = var
            elif ftype == 'textarea':
                w = tk.Text(self.frame, height=3, width=40); w.pack(fill=tk.X); w.insert('1.0', field.get('default', '')); self.inputs[name] = w
            else:
                var = tk.StringVar(value=field.get('default', ''))
                w = ttk.Entry(self.frame, textvariable=var, show='*' if ftype == 'password' else ''); w.pack(fill=tk.X); self.inputs[name] = var
        btn_frame = ttk.Frame(self.frame); btn_frame.pack(pady=20)
        def submit():
            self.result = {}
            for n, w in self.inputs.items():
                if isinstance(w, tk.BooleanVar): self.result[n] = w.get()
                elif isinstance(w, tk.Text): self.result[n] = w.get('1.0', tk.END).strip()
                else: self.result[n] = w.get()
            self.root.quit()
        def cancel(): self.result = {'_cancelled': True}; self.root.quit()
        ttk.Button(btn_frame, text=schema.get('submit_label', 'Submit'), command=submit).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text=schema.get('cancel_label', 'Cancel'), command=cancel).pack(side=tk.LEFT, padx=5)

    def run(self, schema): self.render(schema); self.root.wait_window(); return self.result

gui = None
def gui_main(): global gui; gui = VibeWindow(); gui.root.mainloop()

TOOL = {'name': 'vibe_ui', 'description': 'Show GUI for structured input', 'inputSchema': {'type': 'object', 'properties': {'title': {'type': 'string'}, 'description': {'type': 'string'}, 'fields': {'type': 'array', 'items': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'label': {'type': 'string'}, 'type': {'type': 'string', 'enum': ['text', 'email', 'password', 'number', 'textarea', 'select', 'checkbox']}, 'required': {'type': 'boolean'}, 'default': {'type': 'string'}, 'options': {'type': 'array', 'items': {'type': 'string'}}}, 'required': ['name']}}, 'submit_label': {'type': 'string'}, 'cancel_label': {'type': 'string'}}, 'required': ['fields']}}

def send(msg):
    data = json.dumps(msg)
    sys.stdout.buffer.write(('Content-Length: ' + str(len(data)) + '\r\n\r\n' + data).encode())
    sys.stdout.flush()

async def handle(req):
    m, rid, p = req.get('method'), req.get('id'), req.get('params', {})
    if m == 'initialize':
        send({'jsonrpc': '2.0', 'id': rid, 'result': {'protocolVersion': '2024-11-05', 'capabilities': {'tools': {}}, 'serverInfo': {'name': 'vibescreen', 'version': '0.1.0'}}})
        send({'jsonrpc': '2.0', 'method': 'notifications/initialized', 'params': {}})
    elif m == 'tools/list': send({'jsonrpc': '2.0', 'id': rid, 'result': {'tools': [TOOL]}})
    elif m == 'tools/call':
        if p.get('name') != 'vibe_ui': send({'jsonrpc': '2.0', 'id': rid, 'error': {'message': 'Unknown tool'}}); return
        result = await asyncio.get_event_loop().run_in_executor(None, lambda: gui.run(p.get('arguments', {}).get('schema', {})))
        send({'jsonrpc': '2.0', 'id': rid, 'result': {'content': [{'type': 'text', 'text': json.dumps(result, indent=2)}]}})
    else: send({'jsonrpc': '2.0', 'id': rid, 'error': {'message': 'Unknown method: ' + m}})

def run_server():
    buf, cl = b'', 0
    while True:
        line = sys.stdin.readline()
        if not line: break
        line = line.strip()
        if line.startswith('Content-Length:'):
            cl = int(line.split(':')[1].strip())
            body = sys.stdin.read(cl)
            req = json.loads(body)
            asyncio.run(handle(req))

async def main():
    threading.Thread(target=gui_main, daemon=True).start()
    await asyncio.sleep(0.5)
    await asyncio.get_event_loop().run_in_executor(None, run_server)

if __name__ == '__main__': asyncio.run(main())
