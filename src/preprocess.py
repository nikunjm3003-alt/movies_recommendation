import pandas as pd


def load_and_preprocess(data_path):
    df = pd.read_csv(data_path)

    

    expected = {
        'movieId':      0,
        'title':        'Unknown',
        'year':         0,
        'genres':       '',
        'imdb_rating':  0.0,
        'mood':         '',
        'where_to_watch': ''
    }

    for col, default in expected.items():
        if col not in df.columns:
            df[col] = default

    return df