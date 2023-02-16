#!/usr/bin/env python3

# Author: Peter Smith 2023/02/15

import sys
import os
import threading
import subprocess

from typing import List, Dict


VERSION = "1.0.0"

use_output_colour = True

def eprint(*args, **kwargs):
    print(TermCols.FAIL, file=sys.stderr, end='')
    print(*args, file=sys.stderr, **kwargs)
    print(TermCols.ENDC, file=sys.stderr, end='')
    sys.stderr.flush()

class TermCols:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def set_col(col):
    if not use_output_colour:
        return
    print(col, end="")
    sys.stdout.flush()


def clear_col():
    set_col(TermCols.ENDC)


class RepoUpdater:

    def __init__(self, relative_path: str, absolute_path: str):
        self.relative_path = relative_path
        self.absolute_path = absolute_path
        self.repo_updater_thread = threading.Thread(target=self.thread_handle)
        self.repo_updater_thread.start()
        self.pull_return_code = -1


    def thread_handle(self):
        set_col(TermCols.OKCYAN)
        print("Updating git repo: {}".format(self.relative_path))
        clear_col()

        pull_command_string: str = "cd {}; git pull; git submodule update --init".format(self.absolute_path)
        self.pull_command = subprocess.Popen(pull_command_string, shell=True)

        self.pull_command.wait()
            
        clear_col()
        # print("Waiting for subprocess...")
        self.pull_command.wait()
        self.pull_return_code = self.pull_command.returncode
        # print("Subprocess complete, return code = {}".format(self.pull_return_code))
        
        

class RepoSearcher:

    def __init__(self, working_dir_absolute_path: str):
        self.working_dir_absolute_path = working_dir_absolute_path
        self.repo_updaters: List[RepoUpdater] = []
        self.run()
    

    def run(self):

        print('Searching from root directory:')
        set_col(TermCols.BOLD)
        print('{}/'.format(current_working_dir))
        clear_col()

        relative_path_queue: List[str] = ['']
        

        while(len(relative_path_queue) > 0):
            relative_path = relative_path_queue[0]
            # print('Found {}'.format(current_dir))
            relative_path_queue.pop(0)

            absolute_path = self.working_dir_absolute_path + relative_path
            # print("absolute_path = {}".format(absolute_path))
            sub_dir_files: List[str] = os.listdir(absolute_path)

            # Search for git repos:
            found_git_repo = False
            for sub_dir_name in sub_dir_files:
                if sub_dir_name == ".git":
                    found_git_repo = True
                    break

            if found_git_repo:
                # print("Found git repo: {}".format(current_dir))
                new_repo_updater = RepoUpdater(relative_path, absolute_path)
                self.repo_updaters.append(new_repo_updater)

            else:
                for sub_dir_name in sub_dir_files:
                    relative_sub_dir_path:str = "{}/{}".format(relative_path, sub_dir_name)
                    absolute_sub_dir_path = self.working_dir_absolute_path + '/' + relative_sub_dir_path
                    # print('sub_dir_path = {}'.format(sub_dir_path))
                    if os.path.isdir(absolute_sub_dir_path):
                        relative_path_queue.append(relative_sub_dir_path)

        total_thread_cound = len(self.repo_updaters)
        successful_threads : List[RepoUpdater] = []
        failed_threads : List[RepoUpdater] = []
        # Wait for all threads to finish.
        for repo_updater in self.repo_updaters:
            repo_updater.repo_updater_thread.join()
            if repo_updater.pull_return_code == 0:
                successful_threads.append(repo_updater)
            else:
                failed_threads.append(repo_updater)

        print("")
        set_col(TermCols.BOLD)
        print("Results:")

        if total_thread_cound == 0:
            set_col(TermCols.WARNING)
            print("No git repos found!")
        elif len(failed_threads) is 0:
            set_col(TermCols.OKGREEN)
            print("All git repos updated successfully!")
        elif len(failed_threads) == total_thread_cound:
            set_col(TermCols.FAIL)
            print("Complete Failure! No repos updated... check your internet connection maybe?")
        else:
            set_col(TermCols.OKBLUE)
            print("Successfully updated:")
            for successful_thread in successful_threads:
                print("{}".format(successful_thread.absolute_path))

            print("")
            set_col(TermCols.FAIL)
            eprint("Failed to update:")
            for failed_thread in failed_threads:
                eprint("{}".format(failed_thread.absolute_path))



if __name__ == '__main__':
    print('Pull All Repos Version {}'.format(VERSION))
    current_working_dir = os.getcwd()
    repoSearcher = RepoSearcher(current_working_dir)