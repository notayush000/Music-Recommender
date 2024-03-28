
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


## Support

For any queries, email [Ayush](mailto:ayush.mohapatra47@gmail.com), [Barenya](mailto:barenyamohanty9@gmail.com)
