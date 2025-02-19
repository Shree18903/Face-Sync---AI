from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import imutils
import pickle
import time
import cv2 as cv
import torch
from torchvision import transforms
import numpy as np
from Model import DeePixBiS
import pyttsx3
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

engine = pyttsx3.init()

tfms = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])

faceClassifier = cv.CascadeClassifier('Classifiers/haarface.xml')

currentname = "unknown"
encodingsP = "encodings.pickle"

#
print("[INFO] loading encodings + face detector...")
data = pickle.loads(open(encodingsP, "rb").read())


vs = VideoStream(src=0,framerate=10).start()
# time.sleep(1)

fps = FPS().start()

def speak(text):
    print(text)
    filename="output/output.jpg"
    attachment=open("output/output.jpg","rb") #image folder

    p=MIMEBase('application','octet-stream')
    p.set_payload((attachment).read())

    encoders.encode_base64(p)

    
while True:

	
	frame = vs.read()
	frame = imutils.resize(frame, width=500)
	boxes = face_recognition.face_locations(frame)
	encodings = face_recognition.face_encodings(frame, boxes)
	names = []

	grey = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
	faces = faceClassifier.detectMultiScale(grey, scaleFactor=1.1, minNeighbors=4)
	
	for encoding in encodings:
		
		matches = face_recognition.compare_faces(data["encodings"],
			encoding)
		name = "Unknown" 
		if True in matches:
			
			matchedIdxs = [i for (i, b) in enumerate(matches) if b]
			counts = {}

			
			for i in matchedIdxs:
				name = data["name"][i]
				counts[name] = counts.get(name, 0) + 1

			
			name = max(counts, key=counts.get)

			if currentname != name:
				currentname = name
				print(currentname)

		names.append(name)

	for ((top, right, bottom, left), name) in zip(boxes, names):
		cv.rectangle(frame, (left, top), (right, bottom),
			(0, 255, 225), 2)
		y = top - 15 if top - 15 > 15 else top + 15
		cv.putText(frame, name, (left, y), cv.FONT_HERSHEY_SIMPLEX,
			.8, (0, 255, 255), 2)

		for x, y, w, h in faces:

			faceRegion = frame[y:y + h, x:x + w]
			faceRegion = cv.cvtColor(faceRegion, cv.COLOR_BGR2RGB)

			faceRegion = tfms(faceRegion)
			faceRegion = faceRegion.unsqueeze(0)

		
			names="unknowm"
			
			engine.say(name) 
			if (name =='Mani') :
				print("Mani HERE")
				# engine.say(name)
				files="output/Mani.jpg"
				cv.imwrite(files,frame)
				file="output/output.jpg"
				cv.imwrite(file,frame) 
				speak("output")
				
			elif (name =='jack') :
				print("jack HERE")
				# engine.say(name)
				files="output/jack.jpg"
				cv.imwrite(files,frame)
				file="output/output.jpg"
				cv.imwrite(file,frame) 
				speak("output")
				

			elif (name =='KARUNA') :
				print("KARUNA HERE")
				# engine.say(name)
				files="output/karuna.jpg"
				cv.imwrite(files,frame)
				file="output/output.jpg"
				cv.imwrite(file,frame) 
				speak("output")
			# elif (name =='PRIYA') :
			# 	print("PRIYA HERE")
			# 	# engine.say(name)
			# 	files="output/priya.jpg"
			# 	cv.imwrite(files,frame)
			# 	file="output/output.jpg"
			# 	cv.imwrite(file,frame) 
			# 	speak("output")
				
			else:
				print("UNKNOWN PERSON here")
				files="output/unknown.jpg"
				cv.imwrite(files,frame)
				file="output/output.jpg"
				cv.imwrite(file,frame) 
				speak("output") 
				

	cv.imshow('PERSON IDENTYFICATION', frame)
	engine.runAndWait() 
	key = cv.waitKey(1) & 0xFF

	if key == ord("q"):
		break

	fps.update()

	fps.stop()
	
cv.destroyAllWindows()
vs.stop()
