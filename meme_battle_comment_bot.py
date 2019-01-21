import praw
import config
import time
import re

#reddit authentication
reddit = praw.Reddit(username = config.username, 
                    password = config.password,
                    client_id = config.client_id, 
                    client_secret = config.client_secret,
                    user_agent = "script:comment in every imgur thread:v1.0 (by /u/f1uk3r)")

#amazon season url list
baseUrl = "http://newfagames.com/meme_generator_test/meme_generator/index.html?"
count = 0

while True:
  for submission in reddit.subreddit('PeterPorky').new(limit=10): # increase limit number upto 1000 to run the script for more threads in new
    if submission.domain == "i.imgur.com" or submission.domain == "imgur.com":
      if re.search(r'.\w+', submission.url):
        if submission.comments:
          first_comment = submission.comments[0]
          if not (first_comment.stickied and first_comment.author == 'f1uk3r'):
            imgurCode = re.search(r'https?://i.imgur.com/(\w+.\w+)', submission.url).group(1)
            comment = submission.reply(baseUrl + imgurCode)
            comment.mod.distinguish(how="yes", sticky=True)
        else:
          imgurCode = re.search(r'https?://i.imgur.com/(\w+.\w+)', submission.url).group(1)
          comment = submission.reply(baseUrl + imgurCode)
          comment.mod.distinguish(how="yes", sticky=True)

  time.sleep(60) #sleep code for 60 seconds
  count += 1
  print(count)