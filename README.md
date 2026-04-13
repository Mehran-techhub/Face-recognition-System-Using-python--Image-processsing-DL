# Face-recognition-System-Using-python--Image-processsing-DL



	DOCUMENTARY OF FACE RECOGNITION DETECTION & ATTENDENCE SYSTEM USING HAAR CASCADE:

🔷 Project Overview
This is a FACE RECOGNITION & ATTENDENCE SYSTEM for:
•	Registering users using face images
•	Verifying identity
•	Marking attendance
•	Preventing duplicate registrations
•	Providing a dashboard
•	Supporting theme switching (light/dark)
It uses OpenCV for face detection, pickle and Excel for data storage, and PIL/Matplotlib for image and dashboard visualization.
________________________________________
🔹 1. File & Folder Setup
CODE:
base_path = r"D:\\...\\DIP"
data_file = os.path.join(base_path, "user_data.pkl")
excel_file = os.path.join(base_path, "user_data.xlsx")
attendance_file = os.path.join(base_path, "attendance.xlsx")

________________________________________
🔹 2. CRUD Operations apply on Face Registration:
________________________________________
1. Create User (Registration)
Purpose
Register new users by capturing facial data and storing metadata (name/age).
GUI Access
Register User button → Registration Window
Workflow
1.	User enters Name and Age
2.	Captures 5 face images via webcam
3.	Validates against existing users:
o	Checks for duplicate names (allows override)
o	Compares face histograms to prevent duplicate faces
4.	Stores:
o	Face crops in user_images/
o	Metadata in user_data.pkl (Pickle)
o	Basic info in user_data.xlsx (Excel)
Code Functions
•	register_gui(): Handles GUI input
•	capture_face(mode="register"): Manages face capture logic
________________________________________
2. Read Users (Listing)
Purpose
View all registered users and their ages.
GUI Access
List Users button
Workflow
1.	Loads data from user_data.pkl
2.	Displays formatted list in dialog:
User1 - Age: 25  
User2 - Age: 30  
Code Functions
•	list_users(): Retrieves and formats data
________________________________________
3. Update User
Purpose
Modify the age of an existing user.
GUI Access
Update User button → Name/Age prompt
Workflow
1.	Prompts for existing username
2.	Validates user existence
3.	Prompts for new age
4.	Updates:
o	Pickle file (user_data.pkl)
o	Excel file (user_data.xlsx)
Code Functions
•	update_user(): Handles update logic
Limitations
•	Cannot modify username (requires deletion + re-registration)
•	Age must be numeric
________________________________________
4. Delete User
Purpose
Permanently remove a user from the system.
GUI Access
Delete User button → Name prompt
Workflow
1.	Prompts for username
2.	Validates existence
3.	Deletes:
o	All associated face images from user_images/
o	User entry from user_data.pkl
o	Row from user_data.xlsx
Code Functions
•	delete_user(): Manages deletion
Critical Notes
•	Irreversible operation
•	Physical file deletion from storage
________________________________________
CRUD Implementation Summary Table
Operation	Method	Data Affected	Storage Updated
Create	Registration	Adds new user + 5 images	Pickle, Excel, Image folder
Read	List Users	No modification	-
Update	Age modification	Updates age field	Pickle, Excel
Delete	User removal	Removes user + all images	Pickle, Excel, Image folder
________________________________________
Key Technical Notes:
1.	Data Consistency
o	Changes are simultaneously reflected in both Pickle (programmatic access) and Excel (human-readable format).
2.	Image Management
o	Deletion removes physical .jpg files from user_images/
3.	Validation Rules
o	Age must be integer-convertible
o	Name must exist for Update/Delete operations
4.	Security Considerations
o	No authentication required for CRUD operations
o	Physical image files are unencrypted
________________________________________
Usage Example Flow
1.	Create: Register user "Alice" with age 28 → Captures 5 face images
2.	Read: List shows "Alice - Age: 28"
3.	Update: Change Alice's age to 29
4.	Delete: Remove Alice → All data/images erased

📁 Purpose: Organize storage:
•	user_data.pkl → User face data in binary format.
•	user_data.xlsx → User records (Name, Age).
•	attendance.xlsx → Attendance logs.
•	user_images/ → Cropped face images.
•	detection_images/ → Full frame where face was detected.
________________________________________
🔹 3. Themes
CODE:
THEMES = { "light": {...}, "dark": {...} }
🎨 Purpose: Enables light/dark GUI modes.
________________________________________
🔹 4. Load Haar Cascade
CODE:
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
📷 Used for face detection from video frames (OpenCV).
________________________________________
🔹 5. Data Handling Functions
load_data() and save_data(data)
Load/save user data from/to .pkl using pickle.
save_to_excel(data)
Save user info (name, age) to Excel for easy human reading.
log_attendance(name)
Logs attendance only once per user per day in attendance.xlsx.
________________________________________
🔹 6. Duplicate Face Detection
CODE:
compare_faces(face_img, stored_images)
📌 Uses grayscale histograms to check if a face is already registered by comparing similarity with existing images. If correlation > 0.9 → considered duplicate.
________________________________________
🔹 7. Main Function: capture_face(...)
Handles face capture for:
•	register
•	verify
•	attendance
🔑 Common Steps:
•	Start camera (cv2.VideoCapture(0))
•	Detect face using face_cascade.detectMultiScale()
•	If new face → store cropped image and full frame
•	Hash to avoid duplicate face in the same session
•	Save images and data accordingly
🔁 Modes:
Mode	Purpose	Behavior
"register"	Register new user (with age)	Captures 5 face images
"verify"	Verify face matches name/age	Shows access granted/denied
"attendance"	Logs attendance if valid user	Marks date/time in Excel
________________________________________
🔹 8. GUI with Tkinter
✳️ Basic Layout:
•	root: Main window
•	sidebar: For navigation buttons
•	main_frame: For content area
•	preview_frame: For showing captured face
•	status_label: Status message at bottom
✳️ Windows:
•	register_gui(): Enter name + age, register face
•	verify_gui(): Enter name + age, verify face
•	attendance_gui(): Mark attendance
•	dashboard_gui(): Show attendance summary
________________________________________
🔹 9. Theme Support
CODE:
toggle_theme()
apply_theme(...)Switch between light and dark themes by applying new background/foreground colors dynamically to all widgets.
________________________________________
🔹 10. Image Preview
show_preview(img)


	Key Features Highlight
•	Face detection using Haar Cascade
•	Histogram-based face comparison
•	Data persistence with pickle and Excel
•	Attendance tracking with date/time stamps
•	Duplicate registration prevention
•	GUI with real-time preview
•	CRUD operations for user management

	Important Design Choices
•	Uses multiple validation checks
•	Maintains separate image storage
•	Implements different operation modes
•	Uses Tkinter for lightweight GUI
•	Maintains data consistency across formats
•	Includes error handling for camera access


