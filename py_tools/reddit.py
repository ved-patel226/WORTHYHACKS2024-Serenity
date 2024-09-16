import praw
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
import numpy as np
from .ai import *
from .dbActions import *
from .env_to_var import env_to_var
from termcolor import cprint
import time
import os
from tqdm import tqdm

class reddit:  
    def __init__(self, subreddit:str):
        
        self.subreddit = subreddit
        
        self.reddit = praw.Reddit(
            user_agent=env_to_var("REDDIT_USER_AGENT"),
            client_id=env_to_var("REDDIT_CLIENT_ID"),
            client_secret=env_to_var("REDDIT_CLIENT_SECRET"),
        )

        self.subreddit = self.reddit.subreddit(subreddit)


    def graph(self):
        
        db = DbActions(env_to_var("DB_URL"))
        relevent = db.read("posts", "location", "EdisonNJ")
                
        post_times = []
        for submission in self.subreddit.top():
            if submission.title not in [post[1] for post in relevent]:
                continue
            
            created_utc = submission.created_utc
            created_date = datetime.fromtimestamp(created_utc)
            post_times.append(created_date)
        
        
        
        df = pd.DataFrame(post_times, columns=['created_date'])
        df['created_date'] = pd.to_datetime(df['created_date'], errors='coerce')
        df.dropna(subset=['created_date'], inplace=True)
        df.set_index('created_date', inplace=True)


        daily_posts = df.resample('D').size()

        daily_posts = daily_posts.reindex(pd.date_range(start=daily_posts.index.min(), end=daily_posts.index.max(), freq='D'), fill_value=0)

        x = np.arange(len(daily_posts))
        y = daily_posts.values

        xnew = np.linspace(x.min(), x.max(), 300)
        spl = make_interp_spline(x, y, k=5)
        ynew = spl(xnew)

        dates = daily_posts.index

        dates_new = pd.date_range(start=dates.min(), end=dates.max(), periods=len(xnew))

        plt.figure(figsize=(12, 6))
        plt.plot(daily_posts.index, daily_posts.values, 'o', color='b', label='Daily Posts')
        plt.plot(dates_new, ynew, color='r', linewidth=2, label='Smoothed Curve')

        plt.title('Number of Posts Created per Day')
        plt.xlabel('Date')
        plt.ylabel('Number of Posts')
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f'static/graphs/GRAPH-{round(datetime.now().timestamp())}.png', dpi=300)

        plt.close()

    def get_top_posts(self):
        posts = []
        for submission in self.subreddit.top():
            posts.append([submission.title, submission.selftext, submission.score])
        return posts
    
    def filter(self):    
        posts = self.get_top_posts()
        ai = groq()
        
        relevent_posts = []
        
        db = DbActions(env_to_var("DB_URL"))

        
        for post in tqdm(posts):
            prompt = f"""If the following post is representing a problem in their community
            in any way, please type 'yes'.
            Otherwise, type 'no'
            if not confident in your answer, type 'no'
            Example: Traffic Light Needed at Grove.
            Kids cross this everyday and they need more protection: yes.
            {post[0]}. {post[1]}"""
            
            try:
                response = ai.send_message(prompt)
                time.sleep(0.1)
            except Exception as e:
                print(f"Error sending message: {e}")
                continue

            if response.strip().lower() == "yes":
                db.append([post[0], post[1], post[2], 0, str(self.subreddit)])
            else:
                continue
            
    def find_newest_file(self, PATH):
        
        directory_path = 'static/graphs/'
        
        most_recent_file = None
        most_recent_time = 0
        
        for file in os.scandir(directory_path):
            mod_time = file.stat().st_mtime_ns
            if mod_time > most_recent_time:
                most_recent_file = file.name
                most_recent_time = mod_time
                    
        most_recent_file = "static/graphs/" + most_recent_file
        
        return most_recent_file
    

if __name__ == "__main__":
    reddit = reddit("EdisonNJ")
    
    reddit.filter()
    