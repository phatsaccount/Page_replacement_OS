import heapq
import tkinter as tk
import os
from tkinter import ttk, messagebox, StringVar
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from typing import List, Dict, Any, Optional, Tuple

from replacementFunc import FIFO, LRU, Optimal

# Application color scheme
COLORS = {
    "bg_primary": "#f0f8ff",
    "bg_secondary": "#e1ecf4",
    "accent": "#3498db",
    "text_primary": "#2c3e50",
    "text_light": "#7f8c8d",
    "success": "#2ecc71",
    "warning": "#e74c3c",
    "highlight": "#9b59b6",
    "border": "#bdc3c7"
}

# Visualization color scheme
VIZ_COLORS = {
    "grid_bg": "white",
    "title": "#2c3e50",
    "new_page": "#a1e9c4",
    "existing_page": "#f4f6f7",
    "text": "#34495e",
    "stats_hits": "#27ae60",
    "stats_faults": "#c0392b",
    "stats_ratio": "#2980b9"
}

# Session history for page sequences (only during current session)
page_sequence_history = []


class PageReplacementSimulator:
    """
    Main application class for the Page Replacement Algorithm Simulator.
    """
    
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Page Replacement Algorithm Simulator")
        self.root.configure(bg=COLORS["bg_primary"])
        
        self.root.wm_minsize(1000, 900)
        
        self._configure_styles()
        self._create_layout()
        
        self.canvas_widget = None
        self.graph_canvas = None
    
    def _create_layout(self) -> None:
        main_frame = ttk.Frame(self.root, style="Main.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        self._create_header(main_frame)
        self._create_controls(main_frame)
        self._create_results_area(main_frame)
    
    def _create_header(self, parent: ttk.Frame) -> None:
        header_frame = ttk.Frame(parent, style="Header.TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        title = ttk.Label(
            header_frame, 
            text="Page Replacement Algorithm Simulator", 
            style="Title.TLabel"
        )
        title.pack(pady=10)
        
        description = ttk.Label(
            header_frame,
            text="Visualize and compare different page replacement strategies",
            style="Subtitle.TLabel"
        )
        description.pack(pady=(0, 5))
    
    def _create_controls(self, parent: ttk.Frame) -> None:
        control_frame = ttk.LabelFrame(
            parent, 
            text="Simulation Controls",
            style="Controls.TLabelframe"
        )
        control_frame.pack(fill=tk.X, pady=(0, 15), ipady=10)
        
        input_frame = ttk.Frame(control_frame, style="Main.TFrame")
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(
            input_frame, 
            text="Page Sequence:", 
            style="ControlLabel.TLabel"
        ).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.page_sequence = StringVar()
        self.pages_combobox = ttk.Combobox(
            input_frame, 
            width=50, 
            values=page_sequence_history,
            textvariable=self.page_sequence
        )
        self.pages_combobox.grid(row=0, column=1, sticky=tk.W, padx=(10, 20), pady=5)
        
        ttk.Button(
            input_frame,
            text="?",
            width=2,
            command=self._show_sequence_help
        ).grid(row=0, column=2, padx=(0, 10))
        
        ttk.Label(
            input_frame, 
            text="Frame Size:", 
            style="ControlLabel.TLabel"
        ).grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.frame_size = StringVar(value="3")
        self.frame_size_entry = ttk.Entry(
            input_frame, 
            width=10,
            textvariable=self.frame_size
        )
        self.frame_size_entry.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        ttk.Label(
            input_frame, 
            text="Algorithm:", 
            style="ControlLabel.TLabel"
        ).grid(row=1, column=2, sticky=tk.W, padx=(20, 0), pady=5)
        
        self.algorithm = StringVar(value="Optimal")
        self.algorithm_combobox = ttk.Combobox(
            input_frame,
            values=["FIFO", "LRU", "Optimal"],
            state="readonly",
            width=15,
            textvariable=self.algorithm
        )
        self.algorithm_combobox.grid(row=1, column=3, sticky=tk.W, padx=(10, 0), pady=5)
        
        button_frame = ttk.Frame(control_frame, style="Main.TFrame")
        button_frame.pack(fill=tk.X, padx=20, pady=(10, 5))
        
        run_button = ttk.Button(
            button_frame, 
            text="Run Simulation", 
            command=self.run_simulation,
            style="Accent.TButton"
        )
        run_button.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_button = ttk.Button(
            button_frame, 
            text="Clear", 
            command=self.clear_simulation
        )
        clear_button.pack(side=tk.LEFT)
        
        compare_button = ttk.Button(
            button_frame,
            text="Compare Algorithms",
            command=self._compare_algorithms
        )
        compare_button.pack(side=tk.LEFT, padx=(10, 0))
    
    def _create_results_area(self, parent: ttk.Frame) -> None:
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        self.viz_frame = ttk.Frame(self.notebook, style="Main.TFrame")
        self.notebook.add(self.viz_frame, text="Visualization")
        
        self.canvas_frame = ttk.Frame(self.viz_frame, style="Canvas.TFrame")
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.graph_frame = ttk.Frame(self.notebook, style="Main.TFrame")
        self.notebook.add(self.graph_frame, text="Performance Graph")
        
        self.comparison_frame = ttk.Frame(self.notebook, style="Main.TFrame")
        self.notebook.add(self.comparison_frame, text="Algorithm Comparison")
    
    def _configure_styles(self) -> None:
        style = ttk.Style()
        
        style.configure("Main.TFrame", background=COLORS["bg_primary"])
        style.configure("Header.TFrame", background=COLORS["bg_primary"])
        style.configure("Canvas.TFrame", background=COLORS["bg_secondary"])
        
        style.configure(
            "Title.TLabel", 
            foreground=COLORS["accent"], 
            background=COLORS["bg_primary"], 
            font=("Arial", 16, "bold")
        )
        
        style.configure(
            "Subtitle.TLabel",
            foreground=COLORS["text_light"],
            background=COLORS["bg_primary"],
            font=("Arial", 11)
        )
        
        style.configure(
            "ControlLabel.TLabel", 
            foreground=COLORS["text_primary"], 
            background=COLORS["bg_primary"],
            font=("Arial", 10)
        )
        
        style.configure(
            "Accent.TButton",
            font=("Arial", 10, "bold"),
            background=COLORS["accent"]
        )
        
        style.configure(
            "Controls.TLabelframe",
            background=COLORS["bg_primary"]
        )
        style.configure(
            "Controls.TLabelframe.Label",
            background=COLORS["bg_primary"],
            foreground=COLORS["text_primary"],
            font=("Arial", 11, "bold")
        )
    
    def _show_sequence_help(self) -> None:
        messagebox.showinfo(
            "Page Sequence Help",
            "Enter page references separated by spaces.\n\n"
            "Example: 1 2 3 4 1 2 5 1 2 3 4 5\n\n"
            "This represents a sequence of page requests where "
            "pages 1, 2, 3, 4, etc. are being requested in that order."
        )
    
    def _validate_inputs(self) -> Tuple[bool, List[str], int]:
        pages = self.pages_combobox.get().strip()
        if not pages:
            messagebox.showerror("Error", "Please enter a valid page sequence.")
            return False, [], 0
        
        page_list = pages.split()
        if not page_list:
            messagebox.showerror("Error", "Please enter a valid page sequence.")
            return False, [], 0
        
        frames = self.frame_size_entry.get().strip()
        if not frames.isdigit() or int(frames) <= 0:
            messagebox.showerror("Error", "Frame size must be a positive integer.")
            return False, [], 0
        
        frame_count = int(frames)
        return True, page_list, frame_count
    
    def clear_simulation(self) -> None:
        if hasattr(self, 'canvas_widget') and self.canvas_widget:
            self.canvas_widget.destroy()
            self.canvas_widget = None
        
        if self.graph_canvas:
            self.graph_canvas.get_tk_widget().destroy()
            self.graph_canvas = None
        
        for widget in self.comparison_frame.winfo_children():
            widget.destroy()
        
        status_label = ttk.Label(
            self.canvas_frame,
            text="Visualization cleared. Run a new simulation to see results.",
            style="Subtitle.TLabel"
        )
        status_label.pack(expand=True)
    
    def run_simulation(self) -> None:
        valid, page_list, frame_count = self._validate_inputs()
        if not valid:
            return
        
        algorithm = self.algorithm_combobox.get()
        
        # Add to session history but don't save to file
        pages_text = self.pages_combobox.get().strip()
        if pages_text not in page_sequence_history:
            page_sequence_history.append(pages_text)
            self.pages_combobox['values'] = page_sequence_history
        
        try:
            optional = None
            if algorithm == "FIFO":
                faults, hits, hit_ratio, memory_states = FIFO(page_list, frame_count)
            elif algorithm == "LRU":
                faults, hits, hit_ratio, memory_states = LRU(page_list, frame_count)
            elif algorithm == "Optimal":
                faults, hits, hit_ratio, memory_states, optional = Optimal(page_list, frame_count)
            else:
                messagebox.showerror("Error", "Please select a valid algorithm")
                return
            
            self._plot_memory_states(memory_states, faults, hits, hit_ratio, algorithm, optional)
            self._show_performance_graph()
            
            self.notebook.select(0)
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def _compare_algorithms(self) -> None:
        valid, page_list, frame_count = self._validate_inputs()
        if not valid:
            return
        
        for widget in self.comparison_frame.winfo_children():
            widget.destroy()
        
        try:
            results = {}
            
            fifo_faults, fifo_hits, fifo_ratio, _ = FIFO(page_list, frame_count)
            results["FIFO"] = (fifo_faults, fifo_hits, fifo_ratio)
            
            lru_faults, lru_hits, lru_ratio, _ = LRU(page_list, frame_count)
            results["LRU"] = (lru_faults, lru_hits, lru_ratio)
            
            opt_faults, opt_hits, opt_ratio, _, _ = Optimal(page_list, frame_count)
            results["Optimal"] = (opt_faults, opt_hits, opt_ratio)
            
            self._show_comparison_results(results, page_list, frame_count)
            
            self.notebook.select(2)
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def _show_comparison_results(self, results: Dict[str, Tuple[int, int, float]], 
                                page_list: List[str], frame_count: int) -> None:
        info_frame = ttk.Frame(self.comparison_frame, style="Main.TFrame")
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        sequence_text = " ".join(page_list)
        if len(sequence_text) > 50:
            sequence_text = sequence_text[:47] + "..."
            
        ttk.Label(
            info_frame,
            text=f"Page Sequence: {sequence_text}",
            style="Subtitle.TLabel"
        ).pack(anchor=tk.W)
        
        ttk.Label(
            info_frame,
            text=f"Frame Count: {frame_count}",
            style="Subtitle.TLabel"
        ).pack(anchor=tk.W)
        
        table_frame = ttk.Frame(self.comparison_frame, style="Main.TFrame")
        table_frame.pack(fill=tk.X, padx=10, pady=10)
        
        headers = ["Algorithm", "Page Faults", "Page Hits", "Hit Ratio", "Best For"]
        for col, header in enumerate(headers):
            ttk.Label(
                table_frame,
                text=header,
                style="ControlLabel.TLabel",
                font=("Arial", 11, "bold")
            ).grid(row=0, column=col, padx=10, pady=5, sticky=tk.W)
        
        min_faults = min(results.items(), key=lambda x: x[1][0])
        max_hits = max(results.items(), key=lambda x: x[1][1])
        max_ratio = max(results.items(), key=lambda x: x[1][2])
        
        for row, (algo, (faults, hits, ratio)) in enumerate(results.items(), 1):
            ttk.Label(
                table_frame,
                text=algo,
                style="ControlLabel.TLabel"
            ).grid(row=row, column=0, padx=10, pady=5, sticky=tk.W)
            
            ttk.Label(
                table_frame,
                text=str(faults),
                foreground=COLORS["warning"] if algo == min_faults[0] else COLORS["text_primary"],
                font=("Arial", 10, "bold" if algo == min_faults[0] else "normal")
            ).grid(row=row, column=1, padx=10, pady=5, sticky=tk.W)
            
            ttk.Label(
                table_frame,
                text=str(hits),
                foreground=COLORS["success"] if algo == max_hits[0] else COLORS["text_primary"],
                font=("Arial", 10, "bold" if algo == max_hits[0] else "normal")
            ).grid(row=row, column=2, padx=10, pady=5, sticky=tk.W)
            
            ttk.Label(
                table_frame,
                text=f"{ratio:.2%}",
                foreground=COLORS["accent"] if algo == max_ratio[0] else COLORS["text_primary"],
                font=("Arial", 10, "bold" if algo == max_ratio[0] else "normal")
            ).grid(row=row, column=3, padx=10, pady=5, sticky=tk.W)
            
            best_for = []
            if algo == min_faults[0]:
                best_for.append("Minimizing Faults")
            if algo == max_hits[0]:
                best_for.append("Maximizing Hits")
            if algo == max_ratio[0]:
                best_for.append("Highest Hit Ratio")
                
            ttk.Label(
                table_frame,
                text=", ".join(best_for) if best_for else "-",
                foreground=COLORS["highlight"] if best_for else COLORS["text_light"]
            ).grid(row=row, column=4, padx=10, pady=5, sticky=tk.W)
        
        self._create_comparison_chart(results)
    
    def _create_comparison_chart(self, results: Dict[str, Tuple[int, int, float]]) -> None:
        chart_frame = ttk.Frame(self.comparison_frame, style="Canvas.TFrame")
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        try:
            plt.style.use('seaborn-v0_8-pastel')
        except:
            plt.style.use('seaborn-pastel')
        
        fig = Figure(figsize=(10, 5), dpi=100, facecolor=COLORS["bg_secondary"])
        
        ax1 = fig.add_subplot(121)
        
        algorithms = list(results.keys())
        faults = [results[algo][0] for algo in algorithms]
        hits = [results[algo][1] for algo in algorithms]
        
        x = range(len(algorithms))
        width = 0.35
        
        ax1.bar([i - width/2 for i in x], faults, width, label='Faults', color=COLORS["warning"])
        ax1.bar([i + width/2 for i in x], hits, width, label='Hits', color=COLORS["success"])
        
        ax1.set_ylabel('Page Count')
        ax1.set_title('Faults vs Hits by Algorithm')
        ax1.set_xticks(x)
        ax1.set_xticklabels(algorithms)
        ax1.legend()
        
        ax2 = fig.add_subplot(122)
        
        hit_ratios = [results[algo][2] for algo in algorithms]
        colors = [COLORS["accent"], COLORS["success"], COLORS["highlight"]]
        
        ax2.bar(algorithms, hit_ratios, color=colors[:len(algorithms)])
        
        ax2.set_ylabel('Hit Ratio')
        ax2.set_title('Hit Ratio by Algorithm')
        for i, ratio in enumerate(hit_ratios):
            ax2.text(i, ratio/2, f"{ratio:.2%}", ha='center', va='center', color='white', fontweight='bold')
        
        fig.tight_layout()
        
        comparison_canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        comparison_canvas.draw()
        comparison_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def _show_performance_graph(self) -> None:
        valid, page_list, _ = self._validate_inputs()
        if not valid:
            return
        
        algorithm = self.algorithm_combobox.get()
        
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        
        max_frames = min(15, len(page_list) + 2)
        frame_sizes = list(range(1, max_frames + 1))
        page_faults = []
        
        for frames in frame_sizes:
            try:
                if algorithm == "FIFO":
                    faults, _, _, _ = FIFO(page_list, frames)
                elif algorithm == "LRU":
                    faults, _, _, _ = LRU(page_list, frames)
                elif algorithm == "Optimal":
                    faults, _, _, _, _ = Optimal(page_list, frames)
                else:
                    messagebox.showerror("Error", "Please select a valid algorithm")
                    return
                page_faults.append(faults)
            except Exception as e:
                messagebox.showerror("Error", f"Error calculating faults for frame size {frames}: {str(e)}")
                return
        
        try:
            plt.style.use('seaborn-v0_8-pastel')
        except:
            plt.style.use('seaborn-pastel')
        
        fig = Figure(figsize=(10, 6), dpi=100, facecolor=COLORS["bg_secondary"])
        ax = fig.add_subplot(111)
        
        ax.plot(
            frame_sizes, 
            page_faults, 
            marker="o", 
            label="Page Faults", 
            color=COLORS["warning"], 
            linewidth=2, 
            markersize=8
        )
        
        ax.set_title(
            f"Page Faults vs Frame Size ({algorithm})", 
            fontsize=14, 
            fontweight='bold', 
            color=COLORS["text_primary"]
        )
        ax.set_xlabel("Frame Size", fontsize=12, color=COLORS["text_primary"])
        ax.set_ylabel("Page Faults", fontsize=12, color=COLORS["text_primary"])
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend(fontsize=10)
        
        max_faults = max(page_faults) if page_faults else 0
        ax.set_ylim(0, max_faults * 1.1)
        
        for i, fault in enumerate(page_faults):
            ax.annotate(
                f"{fault}", 
                (frame_sizes[i], fault),
                textcoords="offset points",
                xytext=(0, 10),
                ha='center',
                fontsize=9,
                color=COLORS["text_primary"]
            )
        
        ax.tick_params(colors=COLORS["text_primary"])
        for spine in ax.spines.values():
            spine.set_edgecolor(COLORS["border"])
        
        self._mark_belady_anomalies(ax, frame_sizes, page_faults)
        
        self.graph_canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        self.graph_canvas.draw()
        self.graph_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def _mark_belady_anomalies(self, ax, frame_sizes: List[int], page_faults: List[int]) -> None:
        anomalies = []
        
        for i in range(1, len(frame_sizes)):
            if page_faults[i] > page_faults[i-1]:
                anomalies.append(i)
        
        if anomalies:
            ax.text(
                0.02, 0.02, 
                "Belady's Anomaly detected: More frames caused more page faults!", 
                transform=ax.transAxes,
                color=COLORS["warning"],
                fontsize=10,
                bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5')
            )
            
            for i in anomalies:
                ax.axvspan(
                    frame_sizes[i-1] - 0.2, 
                    frame_sizes[i] + 0.2, 
                    alpha=0.2, 
                    color=COLORS["warning"]
                )
                
                ax.annotate(
                    "Anomaly", 
                    xy=(frame_sizes[i], page_faults[i]),
                    xytext=(frame_sizes[i], page_faults[i] + (max(page_faults) * 0.15)),
                    arrowprops=dict(
                        facecolor=COLORS["warning"], 
                        shrink=0.05,
                        width=2
                    ),
                    fontsize=9,
                    color=COLORS["warning"],
                    ha='center'
                )
    
    def _plot_memory_states(self, memory_states, faults, hits, hit_ratio, algorithm, optional=None) -> None:
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        
        cell_width, cell_height = 40, 60
        offset_x, offset_y = 50, 70
        
        num_columns = len(memory_states)
        canvas_width = max(800, offset_x + num_columns * cell_width + 50)
        canvas_height = offset_y + len(memory_states[0]) * cell_height + 80
        
        self.canvas_widget = tk.Canvas(
            self.canvas_frame, 
            width=canvas_width, 
            height=canvas_height,
            bg=VIZ_COLORS["grid_bg"]
        )
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
        
        self.canvas_widget.create_text(
            canvas_width // 2, 20,
            text=f"Method: {algorithm}", 
            fill=VIZ_COLORS["title"], 
            font=("Arial", 16, "bold")
        )
        
        page_sequence = self.pages_combobox.get().split()
        for step, page in enumerate(page_sequence):
            x = offset_x + step * cell_width
            y = offset_y
            
            self.canvas_widget.create_rectangle(
                x, y - 30, x + cell_width, y - 10,
                fill=COLORS["accent"], 
                outline=""
            )
            
            self.canvas_widget.create_text(
                x + cell_width // 2, y - 20, 
                text=str(page), 
                fill="white", 
                font=("Arial", 12, "bold")
            )
        
        previous_frame = []
        for col, frame in enumerate(memory_states):
            if len(previous_frame) < len(frame):
                previous_frame.extend([None] * (len(frame) - len(previous_frame)))
            
            for row, page in enumerate(frame):
                x = offset_x + col * cell_width
                y = offset_y + row * cell_height
                
                is_new_page = (page not in previous_frame and 
                              page != '-' and page != '_')
                
                cell_color = (VIZ_COLORS["new_page"] if is_new_page 
                             else VIZ_COLORS["existing_page"])
                
                self.canvas_widget.create_rectangle(
                    x, y, x + cell_width, y + cell_height, 
                    outline=COLORS["border"], 
                    fill=cell_color, 
                    width=1.5
                )
                
                display_text = str(page) if page not in ['-', '_'] else "—"
                self.canvas_widget.create_text(
                    x + cell_width // 2, y + cell_height // 2, 
                    text=display_text, 
                    fill=VIZ_COLORS["text"], 
                    font=("Arial", 12, "bold" if is_new_page else "normal")
                )
                
                if (optional and col < len(optional) and 
                   row < len(optional[col]) and optional[col][row] != ''):
                    next_state = optional[col][row]
                    self.canvas_widget.create_text(
                        x + cell_width // 2, y + cell_height - 10, 
                        text=f"{next_state}", 
                        fill=COLORS["highlight"], 
                        font=("Arial", 8)
                    )
            
            previous_frame = frame[:]
        
        self._draw_statistics_box(
            canvas_width, 
            offset_y + len(memory_states[0]) * cell_height + 30,
            faults, hits, hit_ratio
        )
    
    def _draw_statistics_box(self, width: int, y_position: int, 
                            faults: int, hits: int, hit_ratio: float) -> None:
        stats_box_height = 60
        
        self.canvas_widget.create_rectangle(
            20, y_position - 10, 
            width - 20, y_position + stats_box_height,
            fill=COLORS["bg_secondary"], 
            outline=COLORS["border"], 
            width=2
        )
        
        self.canvas_widget.create_text(
            width // 2, y_position + 5,
            text="Performance Statistics", 
            fill=COLORS["text_primary"], 
            font=("Arial", 12, "bold")
        )
        
        self.canvas_widget.create_text(
            width // 4, y_position + 35, 
            text=f"Page Faults: {faults}", 
            fill=VIZ_COLORS["stats_faults"], 
            font=("Arial", 14, "bold")
        )
        
        self.canvas_widget.create_text(
            width // 2, y_position + 35, 
            text=f"Hits: {hits}", 
            fill=VIZ_COLORS["stats_hits"], 
            font=("Arial", 14, "bold")
        )
        
        self.canvas_widget.create_text(
            width * 3 // 4, y_position + 35, 
            text=f"Hit Rate: {hit_ratio:.2%}", 
            fill=VIZ_COLORS["stats_ratio"], 
            font=("Arial", 14, "bold")
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = PageReplacementSimulator(root)
    root.mainloop()