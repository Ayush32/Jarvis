# Speech_Recognition
Welcome to our Python Speech Recognition Tutorial. Its is AI with Python Speech Recognition, we will learn to read an audio file with Python. We will make use of the speech recognition API to perform this task.


Prerequisites for Python Speech Recognition

pip install SpeechRecognition

To test the installation, you can import this in the interpreter and check the version-

>>> import speech_recognition as sr
>>> sr.__version__
‘3.8.1’

We also download a sample audio from here-

http://www.voiptroubleshooter.com/open_speech/american.html

3. Reading an Audio File in Python
a. The Recognizer class
First, we make an instance of the Recognizer class.

Working With Microphones
To be able to work with your own voice with speech recognition, you need the PyAudio package. You can install it with pip-

pip install PyAudio

Or you can download and install the binaries with pip. Download link-

https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

Then:

pip install [file_name_for_binary]

For example:

pip install PyAudio-0.2.11-cp37-cp37m-win32.whl


The Microphone class
Like Recognizer for audio files, we will need Microphone for real-time speech data. Since we installed new packages, let’s exit our interpreter and open another session.

>>> import speech_recognition as sr
>>> r=sr.Recognizer()
Now, let’s create an instance of Microphone.

>>> mic=sr.Microphone()
Microphone has a static method to list out all microphones available-

>>> sr.Microphone.list_microphone_names()
