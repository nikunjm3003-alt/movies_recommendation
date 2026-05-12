import pandas as pd


def load_and_preprocess(data_path):
    df = pd.read_csv(data_path)

    # most of the cleaning is done in my ipynb  file (check that out)

    expected = ['movieId', 'title', 'year', 'genres', 'imdb_rating', 'mood']

    for cols in expected:
        if cols not in df.columns:
            df[cols] = 0

    return df 


