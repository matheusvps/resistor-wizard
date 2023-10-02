# Resistor Wizard Project 🧙‍♂️

## Overview

This GitHub repository hosts the code for the Resistor Sorter project, developed as part of the Integration Workshops 1 course. The system consists of a resistor sorting system that allows users to insert indivual resistors into a small slit and select up to six resistance values to sort them into. The system is implemented as a web application, with its frontend built using CSS, HTML, JavaScript, and React. Both the server and subsequent backend processes are handled by a Raspberry Pi 3B running Flask. Using computer vision techniques, it photographs the resistor's position and extracts color information about the resistor to determine its resistance. Machine Learning (ML) techniques were used to assist in this process.

## Team Members

- **Matheus Passos** - Frontend Development and Project Integration
- **Jhony Minetto** - Backend Development, Algorithm Design and ML Training
- **Ricardo Marthus** - Conception of 3D models and Image Labelling for the dataset

## Project Components

### Frontend

The frontend of the Resistor Sorter project is responsible for creating the user interface where resistors can be input, and resistance values can be selected. The user interacts with the system through this web-based interface.

### Backend

The backend of the project runs on a Raspberry Pi 3B server and is implemented in Python using the Flask framework. It handles the following tasks:

- Determining Resistor's position and color bands location using ML (YOLOv8 network trained on PyTorch ML framework)
- Color recognition using OpenCV
- Communication with the frontend

### Machine-Learning Model

The ML models are a crucial component of this project. They have been trained by our dedicated team to recognize resistors and resistor color bands accurately. The data used to train the models themselves is majoritarily self-provided (meaning we created and labelled the data ourselves). The complete datasets can be visited at <a href="https://universe.roboflow.com/uni-vug0c/metal-film-leaded-resistors-dataset">resistor dataset</a> and <a href="https://universe.roboflow.com/jhony-minetto-arajo/metal-film-leaded-resistor-color-bands">resistor color bands dataset</a>.

## Getting Started

To run this project locally or on your own Raspberry Pi server, follow these steps:

1. Clone this repository: `git clone https://github.com/yourusername/resistor-sorter.git`
2. Set up the frontend environment and dependencies.
   - Navigate to the `frontend` directory.
   - Install dependencies using npm or yarn: `npm install` or `yarn install`.
   - Start the frontend application: `npm start` or `yarn start`.
   
3. Set up the backend environment and dependencies on your Raspberry Pi.
   - Navigate to the `backend` directory.
   - Install Python dependencies: `pip install -r requirements.txt`.
   - Start the Flask server: `python app.py`.
   
4. Ensure the necessary hardware components are connected and configured on your Raspberry Pi for resistor input.

5. Access the web application in your browser and start using the Resistor Sorter.

## Contributions

We welcome contributions and improvements from the community. If you'd like to contribute to this project, please fork the repository, make your changes, and submit a pull request. Your contributions will be greatly appreciated.

Feel free to contact us if you have any questions or need assistance with the project.

Happy sorting!
