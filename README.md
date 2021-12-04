# Flash Card Website
### Created by Vinay Vinod Hariya (21f1006220) 
#### finished on 27<sup>th</sup> November, 2021
<br>

A **flash card** is a card bearing information on both sides, which is intended to be used as an aid in **memorization**. Each flashcard bears a question on one side and an answer on the other. Flashcards are often used to memorize vocabulary, historical dates, formulas or any subject matter that can be learned via a question-and-answer format. Flashcards can be virtual (part of a flashcard software), or physical.

This website helps people study from virtual flash cards. They can create, study, update and even delete flash cards. The Decks can also be made public for other users to benefit from them. All these operations are verified properly via authentication. The website is powered by a simple but robust **API** which makes a good seperation of the backend process from the client application.

The website and API are accessible [here](https://flashcards.vinayhariya.repl.co/).
(**Note**: If the repl is dormant, it may take upto a minute for it to start.)

The website and API are accessible [here](https://flashcards-vinayhariya.glitch.me/).
(**Note**: If the website is dormant, it may take upto 30 seconds for it to start.)

<br>

## Features of the Website:
1. Secure Website - Only registered users can access the decks and the flash cards.
2. Dashboard - Contains all the decks crreated by the user and also a table of all the decks attempted along with links to them for easy access.
3. Ability to Add a new Deck and decide whether to keep it private or public.
4. Update and even Delete decks.
5. For Deck owners, adding, updating and deleting flash cards is easy by accessing them from the deck page. 
6. For public decks, there are only options to view the cards and study them. Thus, the decks are secure.
7. Decks are stored in a relational database with a good schema to prevent problems.
8. There is a scoring system and the time of start is recorded to motivate and show the progress of the user.
9. It is responsive and hence can also be seamlessly used on Mobile Phones.

<br>

## Two main ways to run the code:

#### Note: If you want a fresh database, either rename or delete the flash_db.sqlite3 (under the db_directory inside the api folder)
<br>

1. On the localhost (local machine)
   
   Follow the steps perfectly for successful installation:

   - Ensure python is installed on your system. (Version 3.9 and above)
   - Open the command promt (or equivalent) on the system.
   - Navigate inside to the outer folder housing the project folders and files.
   - Type the following command (instead of ```.env```, you can give any name)
     
     ```
     python -m venv .env
     ```

   - Activate the ```.env``` virutal environment
        - For Windows, type the following
          ```
          .\.env\scripts\activate
          ```
        - For Mac and Linux, type the following
          ```
          source .env/bin/activate
          ```
   - To install all the related packages, type ```pip3```:
     
     ```
     pip3 install -r requirements.txt
     ```

   - Check whether the following lines of code are the same in the main.py (around line 100)
     
     ```
        app.run(host="127.0.0.1", port=8000) # if running on localhost

        # app.run(host="0.0.0.0", port=8080)
     ```

   - Check whether the following lines of code are the same in the config.py inside the application folder. (around line 7)
     
     ```
        HOST = "http://127.0.0.1:8000" # if running on localhost

        # HOST = "replit_host_name_here"
     ```

   - Run the following command to start up the website: (```python3``` for mac and linux users)
     
     ```
     python main.py
     ```


2. On Replit
   
   Follow the steps perfectly for successful installtion:

   - Make an account on [replit](https://replit.com/).
   - Click on ```Create Repl``` button and choose **Python** as the language and give a name to the repl.
   - Delete the empty main.py generated.
   - Paste all the files and folders inside the directory of the repl.
   - Click on the **Packages** option and from the requirements.txt file, copy-paste the names of the packages inside the search box and then install each of them individually. (t prvent an errors with respect to the poetry.lock file)
   - Check whether the following lines of code are the same in the main.py (around line 100)
     
     ```
        # app.run(host="127.0.0.1", port=8000) 

        app.run(host="0.0.0.0", port=8080) # if running on replit
     ```

   - Check whether the following lines of code are the same in the config.py inside the application folder. (around line 7)
     Replace the text within the ```HOST``` variable with the entire domain of your replit (ending in .repl.co) 
     
     ```
        # HOST = "http://127.0.0.1:8000" 

        HOST = "replit_host_name_here" # if running on replit
     ```
   - Click on the Run button to start up the website. Open a new tab and paste the repl full link to access the website.

<br>
<br>
Credentials for login (without registering - for website viewing purpose to gain full understanding of the website):

- user name is ``` Jack Bauer``` and the password is ```abcd1234```

<br>
<br>

## Database Schema

[![database-schema-1.png](https://i.postimg.cc/85Y0GCXw/database-schema-1.png)](https://postimg.cc/MMyDbzSj)
