import cv2
import pickle
import os
import pandas as pd
from datetime import datetime
from tkinter import *
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Custom save path
base_path = r"D:\\smester 5\\5TH SEMESTER PROJECS\\DIP"

# File paths
data_file = os.path.join(base_path, "user_data.pkl")
excel_file = os.path.join(base_path, "user_data.xlsx")
attendance_file = os.path.join(base_path, "attendance.xlsx")
image_folder = os.path.join(base_path, "user_images")
detection_folder = os.path.join(base_path, "detection_images")
os.makedirs(image_folder, exist_ok=True)
os.makedirs(detection_folder, exist_ok=True)

# Theme configurations
THEMES = {
    "light": {
        "bg": "#F5F6F5",
        "fg": "#1A3C34",
        "sidebar_bg": "#1A3C34",
        "sidebar_fg": "white",
        "button_bg": "#2A9D8F",
        "button_fg": "white",
        "preview_bg": "#FFFFFF",
        "status_fg": "#1A3C34"
    },
    "dark": {
        "bg": "#1E1E1E",
        "fg": "#E0E0E0",
        "sidebar_bg": "#2C2C2C",
        "sidebar_fg": "#E0E0E0",
        "button_bg": "#3B82F6",
        "button_fg": "white",
        "preview_bg": "#2C2C2C",
        "status_fg": "#E0E0E0"
    }
}

current_theme = "light"

# Load Haar Cascade
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
if face_cascade.empty():
    raise Exception("Error loading Haar Cascade file.")

# Load user data
def load_data():
    if os.path.exists(data_file):
        with open(data_file, 'rb') as f:
            return pickle.load(f)
    return {}

# Save user data
def save_data(data):
    with open(data_file, 'wb') as f:
        pickle.dump(data, f)

# Save to Excel
def save_to_excel(data):
    df = pd.DataFrame([{"Name": k, "Age": v["age"]} for k, v in data.items()])
    df.to_excel(excel_file, index=False)

# Log attendance
def log_attendance(name):
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    if os.path.exists(attendance_file):
        df = pd.read_excel(attendance_file)
    else:
        df = pd.DataFrame(columns=["Name", "Date", "Time"])

    if not ((df["Name"] == name) & (df["Date"] == date_str)).any():
        new_row = pd.DataFrame([[name, date_str, time_str]], columns=["Name", "Date", "Time"])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_excel(attendance_file, index=False)
        return True
    return False

# Compare faces to prevent duplicates
def compare_faces(face_img, stored_images):
    face_gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
    face_hist = cv2.calcHist([face_gray], [0], None, [256], [0, 256])
    cv2.normalize(face_hist, face_hist)
    
    for stored_path in stored_images:
        if os.path.exists(stored_path):
            stored_img = cv2.imread(stored_path, cv2.IMREAD_GRAYSCALE)
            stored_hist = cv2.calcHist([stored_img], [0], None, [256], [0, 256])
            cv2.normalize(stored_hist, stored_hist)
            correlation = cv2.compareHist(face_hist, stored_hist, cv2.HISTCMP_CORREL)
            if correlation > 0.9:
                return True
    return False

# Capture face for different modes
def capture_face(name, age, mode, num_images=5):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Camera Error", "Cannot access the camera.")
        return

    user_data = load_data()
    captured_count = 0
    processed_faces = set()

    if mode == "register":
        if name in user_data:
            choice = messagebox.askquestion(
                "Name Exists",
                f"The name '{name}' already exists. Do you want to override?"
            )
            if choice == 'yes':
                for img in user_data[name].get("images", []):
                    if os.path.exists(img):
                        os.remove(img)
                user_data[name] = {"age": age, "images": []}
            else:
                new_name = simpledialog.askstring("New Name", "Enter a different name:")
                if not new_name:
                    cap.release()
                    return
                name = new_name
                user_data.setdefault(name, {"age": age, "images": []})
        else:
            user_data.setdefault(name, {"age": age, "images": []})

    while captured_count < num_images:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Error", "Failed to capture frame.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) > 0:
            (x, y, w, h) = max(faces, key=lambda f: f[2] * f[3])
            face_img = frame[y:y + h, x:x + w]
            face_hash = hash(face_img.tostring())

            if face_hash not in processed_faces:
                processed_faces.add(face_hash)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")
                image_path = os.path.join(image_folder, f"{name}_{timestamp}.jpg")
                detection_path = os.path.join(detection_folder, f"{name}_detected_{timestamp}.jpg")

                if mode in ["verify", "attendance"]:
                    all_stored_images = []
                    for user, data in user_data.items():
                        all_stored_images.extend(data.get("images", []))
                    if compare_faces(face_img, all_stored_images):
                        messagebox.showwarning("Duplicate", "This face is already detected.")
                        cap.release()
                        return

                cv2.imwrite(image_path, face_img)
                cv2.imwrite(detection_path, frame)

                if mode == "register":
                    user_data[name]["images"].append(image_path)
                    captured_count += 1
                    show_preview(face_img)

                elif mode == "verify":
                    if name in user_data and user_data[name]["age"] == age:
                        messagebox.showinfo("Access Granted", f"Welcome, {name}!")
                    else:
                        messagebox.showerror("Error", "User not recognized or incorrect age.")
                    cap.release()
                    save_data(user_data)
                    save_to_excel(user_data)
                    return

                elif mode == "attendance":
                    if name in user_data and user_data[name]["age"] == age:
                        if log_attendance(name):
                            messagebox.showinfo("Success", f"{name}'s attendance recorded.")
                        else:
                            messagebox.showinfo("Already Marked", "Attendance already marked today.")
                    else:
                        messagebox.showerror("Error", "User not recognized or incorrect age.")
                    cap.release()
                    save_data(user_data)
                    save_to_excel(user_data)
                    return

        cv2.imshow("Face Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    save_data(user_data)
    save_to_excel(user_data)

    if mode == "register":
        messagebox.showinfo("Success", f"User {name} registered with {captured_count} face samples!")

    cap.release()
    cv2.destroyAllWindows()

# Preview in GUI
def show_preview(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img).resize((200, 200))
    img = ImageTk.PhotoImage(img)
    preview_label.configure(image=img)
    preview_label.image = img

# Toggle theme
def toggle_theme():
    global current_theme
    current_theme = "dark" if current_theme == "light" else "light"
    apply_theme(root, sidebar, main_frame, preview_frame, status_label, preview_label)

# Apply theme to GUI elements
def apply_theme(root, sidebar, main_frame, preview_frame, status_label, preview_label):
    theme = THEMES[current_theme]
    root.config(bg=theme["bg"])
    sidebar.config(bg=theme["sidebar_bg"])
    main_frame.config(bg=theme["bg"])
    preview_frame.config(bg=theme["preview_bg"])
    status_label.config(bg=theme["bg"], fg=theme["status_fg"])
    preview_label.config(bg=theme["preview_bg"])

    for widget in sidebar.winfo_children():
        if isinstance(widget, Label):
            widget.config(bg=theme["sidebar_bg"], fg=theme["sidebar_fg"])
        elif isinstance(widget, Button):
            widget.config(bg=theme["button_bg"], fg=theme["button_fg"])
    
    for widget in main_frame.winfo_children():
        if isinstance(widget, Label) and widget != status_label:
            widget.config(bg=theme["bg"], fg=theme["fg"])
    
    for widget in preview_frame.winfo_children():
        if isinstance(widget, Label) and widget != preview_label:
            widget.config(bg=theme["preview_bg"], fg=theme["fg"])

# Register window
def register_gui():
    window = Toplevel(root)
    window.title("Register User")
    window.geometry("400x400")
    window.config(bg=THEMES[current_theme]["bg"])

    frame = Frame(window, bg=THEMES[current_theme]["bg"])
    frame.pack(pady=20, padx=20, fill=BOTH, expand=True)

    Label(frame, text="Register New User", font=("Helvetica", 16, "bold"), 
          fg=THEMES[current_theme]["fg"], bg=THEMES[current_theme]["bg"]).pack(pady=10)

    Label(frame, text="Name:", font=("Helvetica", 12), 
          fg=THEMES[current_theme]["fg"], bg=THEMES[current_theme]["bg"]).pack(pady=5)
    name_entry = Entry(frame, font=("Helvetica", 12), width=25, bd=1, relief=SOLID)
    name_entry.pack(pady=5)

    Label(frame, text="Age:", font=("Helvetica", 12), 
          fg=THEMES[current_theme]["fg"], bg=THEMES[current_theme]["bg"]).pack(pady=5)
    age_entry = Entry(frame, font=("Helvetica", 12), width=25, bd=1, relief=SOLID)
    age_entry.pack(pady=5)

    Button(frame, text="Register", font=("Helvetica", 12), 
           bg=THEMES[current_theme]["button_bg"], fg=THEMES[current_theme]["button_fg"], 
           width=15, bd=0, command=lambda: do_action(window, name_entry, age_entry, "register")).pack(pady=20)

# Verify window
def verify_gui():
    window = Toplevel(root)
    window.title("Verify User")
    window.geometry("400x400")
    window.config(bg=THEMES[current_theme]["bg"])

    frame = Frame(window, bg=THEMES[current_theme]["bg"])
    frame.pack(pady=20, padx=20, fill=BOTH, expand=True)

    Label(frame, text="Verify User", font=("Helvetica", 16, "bold"), 
          fg=THEMES[current_theme]["fg"], bg=THEMES[current_theme]["bg"]).pack(pady=10)

    Label(frame, text="Name:", font=("Helvetica", 12), 
          fg=THEMES[current_theme]["fg"], bg=THEMES[current_theme]["bg"]).pack(pady=5)
    name_entry = Entry(frame, font=("Helvetica", 12), width=25, bd=1, relief=SOLID)
    name_entry.pack(pady=5)

    Label(frame, text="Age:", font=("Helvetica", 12), 
          fg=THEMES[current_theme]["fg"], bg=THEMES[current_theme]["bg"]).pack(pady=5)
    age_entry = Entry(frame, font=("Helvetica", 12), width=25, bd=1, relief=SOLID)
    age_entry.pack(pady=5)

    Button(frame, text="Verify", font=("Helvetica", 12), 
           bg=THEMES[current_theme]["button_bg"], fg=THEMES[current_theme]["button_fg"], 
           width=15, bd=0, command=lambda: do_action(window, name_entry, age_entry, "verify")).pack(pady=20)

# Attendance window
def attendance_gui():
    window = Toplevel(root)
    window.title("Mark Attendance")
    window.geometry("400x400")
    window.config(bg=THEMES[current_theme]["bg"])

    frame = Frame(window, bg=THEMES[current_theme]["bg"])
    frame.pack(pady=20, padx=20, fill=BOTH, expand=True)

    Label(frame, text="Mark Attendance", font=("Helvetica", 16, "bold"), 
          fg=THEMES[current_theme]["fg"], bg=THEMES[current_theme]["bg"]).pack(pady=10)

    Label(frame, text="Name:", font=("Helvetica", 12), 
          fg=THEMES[current_theme]["fg"], bg=THEMES[current_theme]["bg"]).pack(pady=5)
    name_entry = Entry(frame, font=("Helvetica", 12), width=25, bd=1, relief=SOLID)
    name_entry.pack(pady=5)

    Label(frame, text="Age:", font=("Helvetica", 12), 
          fg=THEMES[current_theme]["fg"], bg=THEMES[current_theme]["bg"]).pack(pady=5)
    age_entry = Entry(frame, font=("Helvetica", 12), width=25, bd=1, relief=SOLID)
    age_entry.pack(pady=5)

    Button(frame, text="Mark Attendance", font=("Helvetica", 12), 
           bg=THEMES[current_theme]["button_bg"], fg=THEMES[current_theme]["button_fg"], 
           width=15, bd=0, command=lambda: do_action(window, name_entry, age_entry, "attendance")).pack(pady=20)

# Attendance dashboard
def dashboard_gui():
    window = Toplevel(root)
    window.title("Attendance Dashboard")
    window.geometry("800x600")
    window.config(bg=THEMES[current_theme]["bg"])

    frame = Frame(window, bg=THEMES[current_theme]["bg"])
    frame.pack(pady=20, padx=20, fill=BOTH, expand=True)

    Label(frame, text="Attendance Dashboard", font=("Helvetica", 16, "bold"), 
          fg=THEMES[current_theme]["fg"], bg=THEMES[current_theme]["bg"]).pack(pady=10)

    # Stats frame
    stats_frame = Frame(frame, bg=THEMES[current_theme]["bg"])
    stats_frame.pack(pady=10, fill=X)

    total_users_label = Label(stats_frame, text="Total Users: 0", font=("Helvetica", 12), 
                             fg=THEMES[current_theme]["fg"], bg=THEMES[current_theme]["bg"])
    total_users_label.pack(side=LEFT, padx=20)

    present_today_label = Label(stats_frame, text="Present Today: 0", font=("Helvetica", 12), 
                               fg=THEMES[current_theme]["fg"], bg=THEMES[current_theme]["bg"])
    present_today_label.pack(side=LEFT, padx=20)

    # Recent logs
    logs_frame = Frame(frame, bg=THEMES[current_theme]["preview_bg"], bd=1, relief=SOLID)
    logs_frame.pack(pady=10, fill=X)
    Label(logs_frame, text="Recent Attendance Logs", font=("Helvetica", 12), 
          bg=THEMES[current_theme]["preview_bg"], fg=THEMES[current_theme]["fg"]).pack(pady=5)
    logs_text = Text(logs_frame, height=5, width=50, font=("Helvetica", 10), 
                     bg=THEMES[current_theme]["preview_bg"], fg=THEMES[current_theme]["fg"])
    logs_text.pack(pady=5)

    # Pie chart
    chart_frame = Frame(frame, bg=THEMES[current_theme]["bg"])
    chart_frame.pack(pady=10, fill=BOTH, expand=True)

    def update_dashboard():
        user_data = load_data()
        total_users = len(user_data)
        today = datetime.now().strftime("%Y-%m-%d")
        
        if os.path.exists(attendance_file):
            df = pd.read_excel(attendance_file)
            present_today = len(df[df["Date"] == today]["Name"].unique())
            recent_logs = df.tail(5)[["Name", "Date", "Time"]].to_string(index=False)
        else:
            present_today = 0
            recent_logs = "No attendance logs available."

        total_users_label.config(text=f"Total Users: {total_users}")
        present_today_label.config(text=f"Present Today: {present_today}")
        logs_text.delete(1.0, END)
        logs_text.insert(END, recent_logs)

        # Update pie chart
        for widget in chart_frame.winfo_children():
            widget.destroy()

        fig, ax = plt.subplots(figsize=(4, 4))
        labels = ['Present', 'Absent']
        sizes = [present_today, max(0, total_users - present_today)]
        colors = ['#2A9D8F', '#E76F51']
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()

        window.after(5000, update_dashboard)  # Refresh every 5 seconds

    update_dashboard()

# List users
def list_users():
    user_data = load_data()
    users = "\n".join([f"{name} - Age: {data['age']}" for name, data in user_data.items()])
    if users:
        messagebox.showinfo("Registered Users", f"List of users:\n\n{users}")
    else:
        messagebox.showinfo("No Users", "No users found.")

# Update user
def update_user():
    name = simpledialog.askstring("Update", "Enter the user's name to update:")
    if not name:
        return
    user_data = load_data()
    if name not in user_data:
        messagebox.showerror("Error", "User not found.")
        return
    new_age = simpledialog.askstring("Update", "Enter new age:")
    if new_age:
        try:
            user_data[name]["age"] = str(int(new_age))
            save_data(user_data)
            save_to_excel(user_data)
            messagebox.showinfo("Success", "User age updated successfully!")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid age.")

# Delete user
def delete_user():
    name = simpledialog.askstring("Delete", "Enter the user's name to delete:")
    if not name:
        return
    user_data = load_data()
    if name in user_data:
        for img_path in user_data[name].get("images", []):
            if os.path.exists(img_path):
                os.remove(img_path)
        del user_data[name]
        save_data(user_data)
        save_to_excel(user_data)
        messagebox.showinfo("Deleted", f"User {name} deleted successfully.")
    else:
        messagebox.showerror("Error", "User not found.")

# Shared logic for actions
def do_action(window, name_entry, age_entry, mode):
    name = name_entry.get().strip()
    age = age_entry.get().strip()
    if name and age:
        try:
            age = str(int(age))
            capture_face(name, age, mode, num_images=1 if mode != "register" else 5)
            window.destroy()
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid age.")
    else:
        messagebox.showerror("Input Error", "Please enter both name and age.")

# Exit the application
def exit_app():
    root.quit()
    cv2.destroyAllWindows()

# GUI Window Setup
root = Tk()
root.title("Face Recognition Attendance System")
root.geometry("800x600")
root.config(bg=THEMES[current_theme]["bg"])

# Sidebar
sidebar = Frame(root, bg=THEMES[current_theme]["sidebar_bg"], width=200)
sidebar.pack(side=LEFT, fill=Y)

# Sidebar Title
Label(sidebar, text="Enroll Users", font=("Helvetica", 15, "bold"), 
      fg=THEMES[current_theme]["sidebar_fg"], bg=THEMES[current_theme]["sidebar_bg"]).pack(pady=16)

# Sidebar Buttons
Button(sidebar, text="Register User", font=("Helvetica", 12), 
       bg=THEMES[current_theme]["button_bg"], fg=THEMES[current_theme]["button_fg"], 
       width=15, bd=0, command=register_gui).pack(pady=10)
Button(sidebar, text="Verify User", font=("Helvetica", 12), 
       bg=THEMES[current_theme]["button_bg"], fg=THEMES[current_theme]["button_fg"], 
       width=15, bd=0, command=verify_gui).pack(pady=10)
Button(sidebar, text="Mark Attendance", font=("Helvetica", 12), 
       bg=THEMES[current_theme]["button_bg"], fg=THEMES[current_theme]["button_fg"], 
       width=15, bd=0, command=attendance_gui).pack(pady=10)
Button(sidebar, text="Attendance Dashboard", font=("Helvetica", 12), 
       bg=THEMES[current_theme]["button_bg"], fg=THEMES[current_theme]["button_fg"], 
       width=15, bd=0, command=dashboard_gui).pack(pady=10)
Button(sidebar, text="Update User", font=("Helvetica", 12), 
       bg=THEMES[current_theme]["button_bg"], fg=THEMES[current_theme]["button_fg"], 
       width=15, bd=0, command=update_user).pack(pady=10)
Button(sidebar, text="Delete User", font=("Helvetica", 12), 
       bg=THEMES[current_theme]["button_bg"], fg=THEMES[current_theme]["button_fg"], 
       width=15, bd=0, command=delete_user).pack(pady=10)
Button(sidebar, text="List Users", font=("Helvetica", 12), 
       bg=THEMES[current_theme]["button_bg"], fg=THEMES[current_theme]["button_fg"], 
       width=15, bd=0, command=list_users).pack(pady=10)
Button(sidebar, text="Toggle Theme", font=("Helvetica", 12), 
       bg=THEMES[current_theme]["button_bg"], fg=THEMES[current_theme]["button_fg"], 
       width=15, bd=0, command=toggle_theme).pack(pady=10)
Button(sidebar, text="Exit", font=("Helvetica", 12), 
       bg=THEMES[current_theme]["button_bg"], fg=THEMES[current_theme]["button_fg"], 
       width=15, bd=0, command=exit_app).pack(pady=10)

# Main Content Area
main_frame = Frame(root, bg=THEMES[current_theme]["bg"])
main_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=20, pady=20)

# Header
Label(main_frame, text="Face Recognition Attendance System", font=("Helvetica", 20, "bold"), 
      fg=THEMES[current_theme]["fg"], bg=THEMES[current_theme]["bg"]).pack(pady=20)

# Preview Area
preview_frame = Frame(main_frame, bg=THEMES[current_theme]["preview_bg"], bd=1, relief=SOLID)
preview_frame.pack(pady=20, fill=X)
Label(preview_frame, text="Face Preview", font=("Helvetica", 12), 
      bg=THEMES[current_theme]["preview_bg"], fg=THEMES[current_theme]["fg"]).pack(pady=5)
preview_label = Label(preview_frame, bg=THEMES[current_theme]["preview_bg"])
preview_label.pack(pady=10)

# Status Area
status_label = Label(main_frame, text="Ready", font=("Helvetica", 12), 
                     fg=THEMES[current_theme]["status_fg"], bg=THEMES[current_theme]["bg"])
status_label.pack(pady=20)

if __name__ == "__main__":
    root.mainloop()