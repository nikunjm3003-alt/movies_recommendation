from preprocess import load_and_preprocess
from recommendation import recommend

def answer():
    df = load_and_preprocess(data_path='data/movies_final.csv')

    results = recommend(
        df, 
        number=5, 
        genre='Animation', 
        mood='Joy', 
        min_year=1990, 
        max_year=2020
    )

    return results

if __name__ == "__main__":
    print(answer())