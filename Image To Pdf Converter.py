import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
from reportlab.pdfgen import canvas
from PIL import Image, ImageTk
import os
from pathlib import Path
import sys

class ImageToPDFConverter:
    def __init__(self, root):
        self.root = root
        self.image_paths = []
        self.output_pdf_name = tk.StringVar(value="output.pdf")
        self.preview_label = None
        self.current_preview_image = None
        self.theme_var = tk.StringVar(value="Default")
        self.initialize_ui()
        self.setup_styles()

    def setup_styles(self):
        style = ttk.Style()
        style.configure("Title.TLabel", 
                       font=("Helvetica", 24, "bold"), 
                       foreground="#2c3e50",
                       padding=10)
        
        style.configure("Accent.TButton", 
                       font=("Helvetica", 10),
                       padding=5)
        
        style.configure("Preview.TLabelframe", 
                       borderwidth=2,
                       relief="solid")

    def initialize_ui(self):
        self.main_container = ttk.Frame(self.root, padding="20")
        self.main_container.pack(fill=tk.BOTH, expand=True)

        self.create_title_section()
        self.create_action_buttons()
        self.create_preview_section()
        self.create_image_list_section()
        self.create_pdf_options()
        self.create_status_bar()
        self.create_theme_selector()

    def create_title_section(self):
        title_label = ttk.Label(
            self.main_container,
            text="Image to PDF Converter",
            style="Title.TLabel"
        )
        title_label.pack(pady=(0, 20))

    def create_action_buttons(self):
        btn_frame = ttk.Frame(self.main_container)
        btn_frame.pack(fill=tk.X, pady=(0, 10))

        select_btn = ttk.Button(
            btn_frame,
            text="Select Images",
            command=self.select_images,
            style="Accent.TButton"
        )
        select_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = ttk.Button(
            btn_frame,
            text="Clear Selection",
            command=self.clear_selection,
            style="Accent.TButton"
        )
        clear_btn.pack(side=tk.LEFT, padx=5)

        self.create_arrange_buttons(btn_frame)

    def create_arrange_buttons(self, parent):
        move_frame = ttk.Frame(parent)
        move_frame.pack(side=tk.RIGHT)

        up_btn = ttk.Button(
            move_frame,
            text="↑",
            command=self.move_image_up,
            width=3
        )
        up_btn.pack(side=tk.LEFT, padx=2)

        down_btn = ttk.Button(
            move_frame,
            text="↓",
            command=self.move_image_down,
            width=3
        )
        down_btn.pack(side=tk.LEFT, padx=2)

    def create_preview_section(self):
        preview_frame = ttk.LabelFrame(
            self.main_container,
            text="Image Preview",
            style="Preview.TLabelframe",
            padding=10
        )
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.preview_label = ttk.Label(preview_frame)
        self.preview_label.pack(pady=10)

    def create_image_list_section(self):
        list_frame = ttk.LabelFrame(
            self.main_container,
            text="Selected Images",
            padding=10
        )
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.selected_images_listbox = tk.Listbox(
            list_frame,
            selectmode=tk.SINGLE,
            yscrollcommand=scrollbar.set,
            height=6,
            activestyle='none'
        )
        self.selected_images_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.selected_images_listbox.yview)

        self.selected_images_listbox.bind('<<ListboxSelect>>', self.show_preview)

    def create_pdf_options(self):
        options_frame = ttk.LabelFrame(
            self.main_container,
            text="PDF Options",
            padding=10
        )
        options_frame.pack(fill=tk.X, pady=10)

        name_frame = ttk.Frame(options_frame)
        name_frame.pack(fill=tk.X)

        ttk.Label(name_frame, text="PDF Name:").pack(side=tk.LEFT)
        ttk.Entry(
            name_frame,
            textvariable=self.output_pdf_name,
            width=40
        ).pack(side=tk.LEFT, padx=5)

        convert_btn = ttk.Button(
            options_frame,
            text="Convert to PDF",
            command=self.convert_images_to_pdf,
            style="Accent.TButton"
        )
        convert_btn.pack(pady=(10, 0))

    def create_status_bar(self):
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(
            self.main_container,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            padding=5
        )
        status_bar.pack(fill=tk.X, pady=(10, 0))

    def create_theme_selector(self):
        theme_frame = ttk.Frame(self.main_container)
        theme_frame.pack(fill=tk.X, pady=10)

        ttk.Label(theme_frame, text="Select Theme:").pack(side=tk.LEFT)
        theme_dropdown = ttk.Combobox(
            theme_frame,
            textvariable=self.theme_var,
            values=["Default", "Dark", "Light"],
            state="readonly"
        )
        theme_dropdown.pack(side=tk.LEFT, padx=5)
        theme_dropdown.bind("<<ComboboxSelected>>", self.change_theme)

    def change_theme(self, event):
        theme = self.theme_var.get()
        if theme == "Default":
            self.root.configure(bg="SystemButtonFace")
        elif theme == "Dark":
            self.root.configure(bg="#2c3e50")
        elif theme == "Light":
            self.root.configure(bg="#ecf0f1")

    def select_images(self):
        files = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff"),
                ("All files", "*.*")
            ]
        )
        
        if files:
            self.image_paths.extend(files)
            self.update_listbox()
            self.status_var.set(f"Added {len(files)} images")

    def update_listbox(self):
        self.selected_images_listbox.delete(0, tk.END)
        for path in self.image_paths:
            filename = os.path.basename(path)
            self.selected_images_listbox.insert(tk.END, filename)

    def show_preview(self, event):
        selection = self.selected_images_listbox.curselection()
        if selection:
            image_path = self.image_paths[selection[0]]
            self.display_preview(image_path)

    def display_preview(self, image_path):
        try:
            img = Image.open(image_path)
            display_size = (300, 300)
            img.thumbnail(display_size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.preview_label.configure(image=photo)
            self.preview_label.image = photo
            self.status_var.set(f"Previewing: {os.path.basename(image_path)}")
            
        except Exception as e:
            messagebox.showerror("Preview Error", f"Error loading image: {str(e)}")
            self.status_var.set("Error loading preview")

    def clear_selection(self):
        self.image_paths = []
        self.selected_images_listbox.delete(0, tk.END)
        self.preview_label.configure(image='')
        self.status_var.set("All images cleared")

    def move_image_up(self):
        selection = self.selected_images_listbox.curselection()
        if not selection or selection[0] == 0:
            return

        index = selection[0]
        self.image_paths[index], self.image_paths[index-1] = \
            self.image_paths[index-1], self.image_paths[index]
        
        self.update_listbox()
        self.selected_images_listbox.selection_set(index-1)
        self.status_var.set(f"Moved {os.path.basename(self.image_paths[index-1])} up")

    def move_image_down(self):
        selection = self.selected_images_listbox.curselection()
        if not selection or selection[0] == len(self.image_paths) - 1:
            return

        index = selection[0]
        self.image_paths[index], self.image_paths[index+1] = \
            self.image_paths[index+1], self.image_paths[index]
        
        self.update_listbox()
        self.selected_images_listbox.selection_set(index+1)
        self.status_var.set(f"Moved {os.path.basename(self.image_paths[index+1])} down")

    def convert_images_to_pdf(self):
        if not self.image_paths:
            messagebox.showwarning("No Images", "Please select images to convert")
            return

        if not self.output_pdf_name.get():
            messagebox.showwarning("No Name", "Please enter a name for the PDF")
            return

        output_path = self.output_pdf_name.get()
        if not output_path.endswith('.pdf'):
            output_path += '.pdf'

        try:
            c = canvas.Canvas(output_path)
            
            for image_path in self.image_paths:
                img = Image.open(image_path)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                    
                img_width, img_height = img.size
                aspect = img_height / float(img_width)
                
                c.setPageSize((img_width, img_height))
                c.drawImage(image_path, 0, 0, width=img_width, height=img_height)
                c.showPage()
            
            c.save()
            
            messagebox.showinfo("Success", f"PDF created successfully: {output_path}")
            self.status_var.set("PDF created successfully")
            
            os.startfile(os.path.dirname(os.path.abspath(output_path)))
            
        except Exception as e:
            messagebox.showerror("Error", f"Error creating PDF: {str(e)}")
            self.status_var.set("Error creating PDF")

def main():
    root = tk.Tk()
    root.title("Image to PDF Converter")
    
    root.geometry("500x800")
    root.minsize(500, 800)
    
    try:
        root.iconbitmap("icon.ico")
    except:
        pass
    
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)
    
    converter = ImageToPDFConverter(root)
    
    root.mainloop()

if __name__ == "__main__":
    main()