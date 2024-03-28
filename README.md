
# Music Recommender

A Web based music recommender written in python.

We built our own music recommendation system using a song dataset. It integrates with the Spotify API to fetch and play songs directly within our web app.



## Features

- Search Songs of your choice.
- Get recommendation based on your listening.


## How to use in your System
- Download and Extract the zip file.

- Create a Spotify developer account ([here](https://developer.spotify.com/)).

- Create an app ([create](https://developer.spotify.com/dashboard/create)) in the dashboard
    - Add a _REDIRECT_URL_ (mandatory)
    - Tick the Web API checkbox 
- After creating the app get the credentials
    -  CLIENT_ID
    -  CLIENT_SECRET

- Open the `api.py` file and paste these credentials 
     ```python
    self.CLIENT_ID     = " "
    self.CLIENT_SECRET = " "
    ```
- Add the _REDIRECT_URL_ in the code as well `api.py ` 
    ```python
    self.REDIRECT_URI = " "
    ```
- Open any of the spotify logged in device. Make sure the device is active as it will play songs on that device.

- Now run `main.py`
    ```python
    python main.py
    ```


## Screenshots
![image](https://github.com/notayush000/Web-Music-Recommender/assets/58353326/8f7f42c3-b4f3-42e4-af87-b46125a2f873)
![image](https://github.com/notayush000/Web-Music-Recommender/assets/58353326/0728c82e-35a2-479d-bb17-fb54de7ec0af)
![image](https://github.com/notayush000/Web-Music-Recommender/assets/58353326/89641a01-e706-42b7-a1f4-02b50196294d)
![image](https://github.com/notayush000/Web-Music-Recommender/assets/58353326/1d9639d9-1b0c-423d-b551-3ea93853756a)
![image](https://github.com/notayush000/Web-Music-Recommender/assets/58353326/9091f254-4027-4eee-a03d-e991584dc0a4)



## Support

For any queries, email [Ayush](mailto:ayush.mohapatra47@gmail.com), [Barenya](mailto:barenyamohanty9@gmail.com)
