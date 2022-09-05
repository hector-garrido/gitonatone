"""
TAKES A METRIC OF A REPO (IN THIS CASE punch_card, THE HOURLY COMMIT HISTORY) 
AND TRANSLATES IT INTO NOTES ACCORDING TO A GIVEN SCALE
"""
################################################################################

from music21 import note, stream, chord
import requests
from dotenv import load_dotenv
import os
import numpy as np

load_dotenv() 
owner = os.getenv('owner')
repo = os.getenv('repo')
metric = os.getenv('metric')

################################################################################

def get_github_repo_stats(owner,repo,metric):
    """
    The Repository statistics API allows you to fetch the data that GitHub uses for visualizing different types of repository activity.
    https://docs.github.com/en/rest/metrics/statistics
    """

    url = f'https://api.github.com/repos/{owner}/{repo}/stats/{metric}'

    out = requests.get(url).json()

    return out


def agg_punch_card(out):
    """
    aggregate data of punch_card metric to get mean number of commits per weekday
    for every hour
    """

    commits = []
    for i in range(24):    
        aux = sum([x[2] for x in out if x[1]==i])/7
        aux = np.floor(aux)
        commits.append(aux)
    commits = [int(x)-1 for x in commits]

    # we move it, as lots of us make commits past midnight but not at 5am
    commits = commits[5:] + commits[:5]
    return commits


def build_song(commits,scale,out_name):
    """
    build a song taking your total of commit entries for each period and a
    scale for reference
    output is a midi file
    """

    scale_length = len(scale)

    notes = []
    for x in commits:
        if x==-1:
            notes+='-'
        else:
            if scale[x%scale_length][1]=='#':
                base_note = scale[x%scale_length][:2]
                level = x//scale_length + int(scale[x%scale_length][2])
            else:
                base_note = scale[x%scale_length][0]
                level = x//scale_length + int(scale[x%scale_length][1])
            x = base_note+str(level)
            notes.append(x)

    s = stream.Stream()
    for x in notes:
        if x=='-':
            s.append(note.Unpitched())
        else:
            s.append(note.Note(x))

    s.write('midi',fp=f'{out_name}.midi')
    print(notes)

################################################################################

def run():
    """
    a little demo
    """

    out = get_github_repo_stats(owner,repo,metric)

    commits = agg_punch_card(out)
    print(commits)

    scales = {
    'C':['C3','D3','E3','F3','G3','A3','B3'],
    'a':['A3','B3','C4','D4','E4','F4','G4']
    }

    for key, scale in scales.items():
        build_song(commits,scale,f'{owner}_{repo}_{metric}_{key}_song')    

if __name__ == '__main__':
    run()