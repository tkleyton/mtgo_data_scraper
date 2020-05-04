# MTGO log scrapper
Read [MTGO (Magic: The Gathering Online)](https://magic.wizards.com/en/mtgo) log files and scrape matches information.

**This is an ongoing project!**

## Current status
The module `match_record` can successfully read the Match_GameLog*.dat files, extract some information and dump as json for 1v1 matches.
There are still rare cases which I didn't test. For instance, I don't know what happens when a player mulligans to zero.

Extracted information:
- players' names
- cards played by each player
- date
- for each game:
  - who's on the play
  - who won
  - how many cards each player started with
  - what was the last turn
  
 ## How to use
 - *Where can I find my matches?*
 
 Wizards hides it very well. Navigate to
 ```
 "Users/<your_user>/Local Settings/Application Data/Apps/2.0/Data"
 ```
 and search for `Match_GameLog*.dat` files.
 
 - *I want to do some analysis with pandas, but it's in JSON*
 
 If converting everything to RDBMS formats makes this significantly better, then I'll do it. Until then, I've found that it's not too hard to [flatten those JSON files into pandas DataFrames.](https://www.kaggle.com/jboysen/quick-tutorial-flatten-nested-json-in-pandas)
  
 ## To-do list
 - [ ] separate cards seen by game (so we can check key cards/cards correlation to wins)
 - [ ] improve safety (catch more exceptions)
 - [ ] load previous data so it doesn't have to scrap everything everytime
 - [ ] database integration instead of dumping to a file (MongoDB maybe?)
 - [ ] build deck archetypes database for automatic detection
 - [ ] improve data analysis and eventually deploy with Streamlit or Flask
 - [ ] automatically find the logs folder
