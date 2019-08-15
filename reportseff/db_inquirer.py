import subprocess
from abc import ABC, abstractmethod
from typing import List, Dict
import datetime


class Base_Inquirer(ABC):
    def __init__(self):
        '''
        Initialize a new inquirer
        '''

    @abstractmethod
    def get_valid_formats(self) -> List[str]:
        '''
        Get the valid formatting options supported by the inquirer.
        Return as list of strings
        '''

    @abstractmethod
    def get_db_output(self, columns: List[str],
                      jobs: List[str]) -> List[Dict[str, str]]:
        '''
        Query the databse with the supplied columns
        Format output to be a list of rows, where each row is a dictionary
        with the columns as keys and entries as values
        Output order is not garunteed to match the jobs list
        '''

    @abstractmethod
    def set_user(self, user: str):
        '''
        Set the collection of jobs based on the provided user
        '''


class Sacct_Inquirer(Base_Inquirer):
    '''
    Implementation of Base_Inquirer for the sacct slurm function
    '''
    def __init__(self):
        self.default_args = 'sacct -P -n'.split()
        self.user = None

    def get_valid_formats(self):
        command_args = 'sacct --helpformat'.split()
        result = subprocess.run(
            args=command_args,
            stdout=subprocess.PIPE,
            encoding='utf8',
            check=True,
            universal_newlines=True)
        if result.returncode != 0:
            raise Exception('Error retrieving sacct options with --helpformat')
        result = result.stdout.split()
        return result

    def get_db_output(self, columns, jobs, debug=False):
        '''
        Assumes the columns have already been validated.
        if debug is set, returns the subprocess result as
        the second element of tuple
        '''
        args = self.default_args + [
            '--format=' + ','.join(columns)
        ]

        if self.user:
            start_date = datetime.date.today() - datetime.timedelta(days=7)
            args += [
                f'--user={self.user}',
                f'--starttime={start_date.strftime("%m%d%y")}'  # MMDDYY
            ]
        else:
            args += ['--jobs=' + ','.join(jobs)]

        result = subprocess.run(
            args=args,
            stdout=subprocess.PIPE,
            encoding='utf8',
            check=True,
            universal_newlines=True)

        if result.returncode != 0:
            raise Exception('Error running sacct!')

        lines = result.stdout.split('\n')
        result = [dict(zip(columns, line.split('|')))
                  for line in lines if line]

        if debug:
            return result, '\n'.join(lines)

        return result

    def set_user(self, user: str):
        '''
        Set the collection of jobs based on the provided user
        '''
        self.user = user