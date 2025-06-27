import cv2																# Image recognition
from PIL import Image, ImageTk											# Displaying images
from tkinter import Tk, Toplevel, N, E, S, W, filedialog, messagebox	# Window creation/management
from tkinter.ttk import Button, Label, Frame							# tkinter widgets

cascPath = "assets\\haarcascade_frontalface_default.xml"				# Facial recognition params
faceCascade = cv2.CascadeClassifier(cascPath)							# Facial recognition obj
images = []																# Cropped images
tk_images = []															# Above, but the tkinter version
stupid = []																# Keeps images from being trashed early
global image_num														# Keeps track of which detected face is selected
image_num = 0															# See above

def open_image():
	"""Opens a file selection box and asks the user to select an image
	"""
	global imageCV
	imagePath = filedialog.askopenfilename(title="Open Image File", filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.ico")])
	if imagePath:
		imageCV = cv2.imread(imagePath)
		prev_temp = Image.open(imagePath)								# Creates a small preview image for the user's benefit
		prev_w = prev_temp.width
		prev_h = prev_temp.height
		const = 0
		if prev_h > prev_w:
			const = prev_h / 400
		else:
			const = prev_w / 400
		prev_temp = prev_temp.resize((int(prev_w//const), int(prev_h//const)))
		preview_image = ImageTk.PhotoImage(image=prev_temp)
		img_prev.config(image=preview_image)
		stupid.append(preview_image)									# Adds the photo to a junk array (tkinter will delete it from memory otherwise)
		img_prev.update()

		crop_image()
	else:
		pass															# Makes sure the script doesn't have a fit if nothing is selected

def save_image():
	"""Opens a file selection box so the user can save the cropped image
	"""
	name = filedialog.asksaveasfilename(defaultextension='.jpg', 		# Asks the user to select a place and name for the file
	filetypes=[('JPEG Image', '*.jpg')])								# I split this over 2 lines for formatting

	image_index = image_num
	
	images[image_index].save(name)										# Saves the image under the user-generated name

def choose_image():
	"""Creates a sub-window wherein the user can look through all of the detected faces and save the one they want
	"""
	resetButton.grid(row=2, column=1)
	max = len(images) - 1
	def next_img():
		"""Shows (and selects) the next detected face
		"""
		global image_num
		if image_num >= max:
			image_num = 0
		else:
			image_num += 1
		
		image_label.config(image=tk_images[image_num])
		image_label.update()

	def prev_img():
		"""Shows (and selects) the previous detected face
		"""
		global image_num
		if image_num <= -1:
			image_num = max
		else:
			image_num -= 1
		
		image_label.config(image=tk_images[image_num])
		image_label.update()

	def chooser_exit():
		"""Exits the chooser window
		"""
		chooser.destroy()
	
	chooser = Toplevel(root)											# Sets up a subwindow to choose the photo
	chooser.title('Select the face:')
	chooser.iconbitmap('assets\\passport.ico')
	mainframe_new = Frame(chooser, padding="3 3 12 12")
	mainframe_new.grid(column=0, row=0, sticky=(N, W, E, S))
	chooser.columnconfigure(0, weight=1)
	chooser.rowconfigure(0, weight=1)

	image_label = Label(mainframe_new, image=tk_images[image_num])
	save_button = Button(mainframe_new, text="Save", command=save_image)
	next_button = Button(mainframe_new, text="Next image", command=next_img)
	prev_button = Button(mainframe_new, text="Previous image", command=prev_img)
	chooser_exit_button = Button(mainframe_new, text='Exit', command=chooser_exit)

	image_label.grid(row=0, column=0, columnspan=3)
	save_button.grid(row=1, column=1)
	next_button.grid(row=1, column=2)
	prev_button.grid(row=1, column=0)
	chooser_exit_button.grid(row=2, column=1)

def crop_image():
	"""Uses OpenCV to detect faces within the selected photo, converts them to both a PIL image (for saving) and a tkinter image (for viewing)
	"""
	gray = cv2.cvtColor(imageCV, cv2.COLOR_BGR2GRAY)
	faces = faceCascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(25, 25))

	if len(faces) > 0:
		uploadButton.grid_forget()
		for (x, y, width, height) in faces:								# Crops each image and converts it to a PIL image (for use with tkinter)
			x -= 375													# Adjusts the image to be slightly zoomed out from the face
			y -= 450
			width += 750
			height += 750

			crop_img = imageCV[y:y+height, x:x+width].copy()			# Crops the image, converts it to a Pillow image, and resizes it to 800 x 800 px
			to_convert = cv2.cvtColor(crop_img, cv2.COLOR_BGR2RGB)
			pil_image = Image.fromarray(to_convert)
			pil_image = pil_image.resize((800, 800))
			images.append(pil_image)
			tk_images.append(ImageTk.PhotoImage(image=pil_image.resize((400, 400))))
			chooseButton.grid(row=1, column=1)
	else:																# Handles if there are no faces found
		messagebox.showerror('No Faces!', 'Error: No faces were detected.  Please try a different image.')

def reset():
	"""Resets the program to the beginning state if the user wants to crop a new photo
	"""
	images.clear()
	tk_images.clear()
	stupid.clear()
	img_prev.config(image=placeholder_img)
	uploadButton.grid(row=1, column=1)
	chooseButton.grid_forget()
	resetButton.grid_forget()
	global image_num
	image_num = 0
	for widget in root.winfo_children(): 								# Looping through widgets in main window
		if '!toplevel' in str(widget): 									# If toplevel exists in the item
			widget.destroy()
	root.focus_force()

root = Tk()																# Sets up the tkinter window
root.title('Cropping Tool')
root.iconbitmap("assets\\passport.ico")									# Icon by yoyonpujiono on flaticon.com

mainframe = Frame(root, padding="3 3 12 12")							# Sets up the grid for use in positioning
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

def exit_win():															# This function has to be down here, as a window must be initialized to properly define it
	root.destroy()

placeholder_img = ImageTk.PhotoImage(image=Image.open('assets\\placeholder.png'))
img_prev = Label(mainframe, image=placeholder_img)
uploadButton = Button(mainframe, text="Upload photo", command=open_image)
chooseButton = Button(mainframe, text='Choose face', command=choose_image)
exitButton = Button(mainframe, text='Exit', command=exit_win)
resetButton = Button(mainframe, text="Reset", command=reset)

uploadButton.grid(row=1, column=1)
img_prev.grid(row=0, column=0, columnspan=3)
exitButton.grid(row=3, column=1)

root.mainloop()															# Calls the window loop