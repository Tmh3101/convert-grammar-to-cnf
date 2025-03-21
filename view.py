import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import time

from grammar_processor import (
    read_grammar_from_file,
    to_string,
    remove_useless_sysbols,
    remove_epsilon_rule,
    remove_unit_rule,
    convert_to_cnf
)

class GrammarProcessorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Grammar Processor")
        self.root.geometry("1200x600")
        
        # Variables
        self.current_file = None
        self.grammar = None
        self.start_symbol = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Control Panel
        control_frame = ttk.Frame(self.root, padding="5")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
                
        # Create colored buttons using regular tk.Button
        tk.Button(control_frame, text="Chọn File", command=self.load_file, 
                 bg='#007bff', fg='white', activebackground='#0056b3').pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Thực hiện", command=self.process_grammar,
                 bg='#28a745', fg='white', activebackground='#1e7e34').pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Xóa", command=self.clear_all,
                 bg='#6c757d', fg='white', activebackground='#545b62').pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Thoát", command=self.root.quit,
                 bg='#dc3545', fg='white', activebackground='#c82333').pack(side=tk.RIGHT, padx=5)
        
        # Main Content Area
        content_frame = ttk.Frame(self.root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create left and right frames
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Input Area (Left top)
        input_frame = ttk.LabelFrame(left_frame, text="Văn phạm đầu vào", padding="5")
        input_frame.pack(fill=tk.BOTH, expand=False)
        self.input_text = ScrolledText(input_frame, wrap=tk.WORD, width=40, height=15)
        self.input_text.pack(fill=tk.BOTH, expand=True)
        
        # Output Area (Left bottom)
        output_frame = ttk.LabelFrame(left_frame, text="Văn phạm đầu ra (CNF)", padding="5")
        output_frame.pack(fill=tk.BOTH, expand=False)
        self.output_text = ScrolledText(output_frame, wrap=tk.WORD, height=15)
        self.output_text.bind("<Key>", lambda e: "break")  # Prevent keyboard input
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Step Output & Timing
        step_output_frame = ttk.LabelFrame(right_frame, text="Các bước thực hiện", padding="5")
        step_output_frame.pack(fill=tk.BOTH, expand=False)
        self.step_output = ScrolledText(step_output_frame, wrap=tk.WORD, height=32)
        self.step_output.bind("<Key>", lambda e: "break")  # Prevent keyboard input
        self.step_output.pack(fill=tk.BOTH, expand=True)
        
    def load_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.current_file = file_path
            try:
                with open(file_path, 'r') as file:
                    content = file.read()
                    self.input_text.delete(1.0, tk.END)
                    self.input_text.insert(tk.END, content)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")
                
    def clear_all(self):
        self.input_text.delete(1.0, tk.END)
        self.output_text.delete(1.0, tk.END)
        self.step_output.delete(1.0, tk.END)
        self.current_file = None
        self.grammar = None
        self.start_symbol = None
        
    def process_grammar(self):
        if not self.current_file:
            messagebox.showwarning("Warning", "Please select a file first!")
            return
            
        try:
            # Clear previous results
            self.output_text.delete(1.0, tk.END)
            self.step_output.delete(1.0, tk.END)
            
            # Read grammar
            start_time = time.time()
            self.grammar, self.start_symbol = read_grammar_from_file(self.current_file)
            read_time = time.time() - start_time
            self.step_output.insert(tk.END, f"Đọc văn phạm - {read_time:.6f} giây\n\n")
            
            # Remove useless symbols
            start_time = time.time()
            self.grammar = remove_useless_sysbols(self.grammar, self.start_symbol)
            useless_time = time.time() - start_time
            self.step_output.insert(tk.END, f"Loại bỏ các ký hiệu vô ích - {useless_time:.6f} giây:\n")
            self.step_output.insert(tk.END, to_string(self.grammar, self.start_symbol) + "\n\n")
            
            # Remove epsilon rules
            start_time = time.time()
            self.grammar = remove_epsilon_rule(self.grammar, self.start_symbol)
            epsilon_time = time.time() - start_time
            self.step_output.insert(tk.END, f"Loại bỏ luật sinh epsilon - {epsilon_time:.6f} giây:\n")
            self.step_output.insert(tk.END, to_string(self.grammar, self.start_symbol) + "\n\n")
            
            # Remove unit rules
            start_time = time.time()
            self.grammar = remove_unit_rule(self.grammar, self.start_symbol)
            unit_time = time.time() - start_time
            self.step_output.insert(tk.END, f"Loại bỏ luật sinh đơn vị - {unit_time:.6f} giây:\n")
            self.step_output.insert(tk.END, to_string(self.grammar, self.start_symbol) + "\n\n")
            
            # Convert to CNF
            start_time = time.time()
            cnf_grammar = convert_to_cnf(self.grammar, self.start_symbol)
            cnf_time = time.time() - start_time
            self.step_output.insert(tk.END, f"Chuyển sanh dạng chuẩn Chomsky (CNF) - {cnf_time:.6f} seconds:\n")
            self.step_output.insert(tk.END, to_string(cnf_grammar, self.start_symbol))
            
            # Display final result
            result = to_string(cnf_grammar, self.start_symbol)
            self.output_text.insert(tk.END, result)
            
        except Exception as e:
            messagebox.showerror("Error", f"Processing failed: {str(e)}")

def main():
    root = tk.Tk()
    app = GrammarProcessorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()