import sys
import os


sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from preprocess import load_and_preprocess
from recommendation import recommend


def answer():
    df = load_and_preprocess(data_path='data/movies_final.csv')

    print(f"📋 Columns in df: {df.columns.tolist()}\n")

    results = recommend(
        df,
        number=5,
        genre='Animation',
        mood='Joy',
        min_year=1990,
        max_year=2020,
        min_rating=1.0,
        max_rating=10.0
    )

    if isinstance(results, str):
        print(f"⚠️  No results: {results}")
    else:
        print(f"✅ {len(results)} movies found:\n")
        print(results.to_string(index=False))

    return results


if __name__ == "__main__":
    answer()