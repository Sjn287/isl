import speech_recognition as sr
import numpy as np
import matplotlib.pyplot as plt
import pocketsphinx
from easygui import buttonbox
import os
from PIL import Image, ImageTk
from itertools import count
import tkinter as tk
import string

# Static paths for ISL GIFs and letters
ISL_GIF_PATH = r'C:\sih\static\ISL_Gifs\\'
LETTERS_PATH = r'C:\sih\static\letters\\'

def func():
    r = sr.Recognizer()
    ISL_Gifs = ['help', 'nice to meet you', 'good morning', 'thank you']
    
    arr = [chr(c) for c in range(ord('a'), ord('z') + 1)]
    
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        while True:
            print('Say something')
            audio = r.listen(source)
            try:
                a = r.recognize_sphinx(audio)
                print("You said: " + a.lower())
                
                # Remove punctuation
                a = a.translate(str.maketrans('', '', string.punctuation))
                
                if a.lower() in ['goodbye', 'good bye', 'bye']:
                    print("Oops! Time to say goodbye")
                    break
                
                elif a.lower() in ISL_Gifs:
                    class ImageLabel(tk.Label):
                        def load(self, im):
                            if isinstance(im, str):
                                im = Image.open(im)
                            self.loc = 0
                            
                            self.frames = []
                            try:
                                for i in count(1):
                                    self.frames.append(ImageTk.PhotoImage(im.copy()))
                                    im.seek(i)
                            except EOFError:
                                pass
                            self.delay = im.info.get('duration', 100)
                            if len(self.frames) == 1:
                                self.config(image=self.frames[0])
                            else:
                                self.next_frame()

                        def unload(self):
                            self.config(image=None)
                            self.frames = None

                        def next_frame(self):
                            if self.frames:
                                self.loc += 1
                                self.loc %= len(self.frames)
                                self.config(image=self.frames[self.loc])
                                self.after(self.delay, self.next_frame)

                    root = tk.Tk()
                    lbl = ImageLabel(root)
                    lbl.pack()
                    gif_path = os.path.join(ISL_GIF_PATH, f'{a.lower()}.gif')
                    if os.path.isfile(gif_path):
                        lbl.load(gif_path)
                        root.mainloop()
                    else:
                        print(f"GIF file '{gif_path}' not found.")
                
                else:
                    for i in a.lower():
                        if i in arr:
                            image_path = os.path.join(LETTERS_PATH, f'{i}.jpg')
                            if os.path.isfile(image_path):
                                ImageItself = Image.open(image_path)
                                ImageNumpyFormat = np.asarray(ImageItself)
                                plt.imshow(ImageNumpyFormat)
                                plt.draw()
                                plt.pause(0.8)
                            else:
                                print(f"Image file '{image_path}' not found.")
                    plt.close()

            except sr.UnknownValueError:
                print("Sorry, I did not understand the audio")
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
            except Exception as e:
                print(f"An error occurred: {e}")
            finally:
                plt.close()

while True:
    image = r"C:\sih\static\signlang.png"  # Ensure this image exists in your working directory
    msg = "HEARING IMPAIRMENT ASSISTANT"
    choices = ["Live Voice", "All Done!"]
    reply = buttonbox(msg, image=image, choices=choices)
    if reply == choices[0]:
        func()
    elif reply == choices[1]:
        break