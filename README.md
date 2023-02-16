# GitRepoUpdater
Pulls all the repos in a directory in a multi-threaded way to save you time!

# To use:
cd to the directory of your choice, all git repos you want to update should be subdirectories of this.

Run the script.

# How it works
From your current working directory, it will perform a depth first search to find directories that contain `.git`
In a subprocess it will peform the following:
```
cd {absolute_path}
git pull
git submodule update --init
```
