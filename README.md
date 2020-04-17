# mtgo_data_scrapper
Read MTGO log files and scrap matches information.

**This is an ongoing project!**

## Current status
The module `match_record` can successfully read the Match_GameLog*.dat files, extract some information and dump as json for 1v1 matches.
There are still rare cases which I didn't test. For instance, I don't what happens when a player mulligans to zero.

Extracted information:
- players' names
- cards played by each player
- date
- for each game:
  - who's on the play
  - who won
  - how many cards each player started with
  - what was the last turn
  
 ## To-do list
 - [ ] improve safety (catch more exceptions)
 - [ ] load previous data so it doesn't have to scrap everything everytime
 - [ ] database integration instead of dumping to a file (MongoDB maybe?)
 - [ ] build deck archetypes database for automatic detection
 - [ ] improve data analysis and eventually deploy with Streamlit or Flask
