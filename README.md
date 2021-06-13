# Set of personal scripts to make life less painful

*  `scripts/screen_brightness_control.py` adjusts all screens' brightness depending on the time of day
    
    ```
    # crontab -e
    
    */2 * * * * .../scripts/screen_brightness_control.py
    ```