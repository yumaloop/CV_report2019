#!/bin/bash

echo -e "\033[0;32mDeploying updates to GitHub...\033[0m"


# Go To .git folder
cd ~/workspace/CV_report2019

# Add changes to git.
git add .

# Commit changes.
msg="update repo `date`"
if [ $# -eq 1 ]
  then msg="$1"
fi
git commit -m "$msg"

# Push source and build repos.
git push origin master

# Come Back up to the Project Root
cd ..

# Commit source repository changes
git add .
git commit -m "$msg"
git push origin master