def recommend(df, number, genre, mood, min_year, max_year):

    mask = (
        (df['mood'].str.contains(mood, case=False, na=False)) &
        (df['genres'].str.contains(genre, case=False, na=False)) &
        (df['year'] >= min_year) &
        (df['year'] <= max_year)
    )

    filtered = df[mask]

    if filtered.empty:
        return "No movies found matching those criteria!"

    return filtered.sort_values('imdb_rating', ascending=False) \
                   [['title', 'year', 'genres', 'imdb_rating', 'where_to_watch']] \
                   .head(number)