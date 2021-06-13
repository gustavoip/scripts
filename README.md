# Set of personal scripts to make life less painful

*  `scripts/screen_brightness_control.py` adjusts all screens' brightness depending on the time of day
    
    ```
    # crontab -e
    
    */2 * * * * .../scripts/screen_brightness_control.py
    ```
   **Issues**: in Manjaro you have to disable `Night Color` (it overwrites our previous changes). In other distributions 
   with the same kind of feature, probably the same behavior will happen.

      
      