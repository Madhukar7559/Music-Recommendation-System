import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from textblob import TextBlob
import re
def content_filtering(playlistDF_test):
    playlistDF = pd.read_csv("bigdata.csv")
    print(playlistDF.columns)
    playlistDF.head()

    playlistDF[['artist_name','track_name','name']]




    def drop_duplicates(df):
        df['artists_song'] = df.apply(lambda row: row['artist_name']+row['track_name'],axis = 1)
        return df.drop_duplicates('artists_song')

    songDF = drop_duplicates(playlistDF)
    print("Are all songs unique: ",len(pd.unique(songDF.artists_song))==len(songDF))


    def select_cols(df):
           return df[['artist_name','id','track_name','danceability', 'energy', 'key', 'loudness', 'mode','speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', "artist_pop", "genres", "track_pop"]]
    songDF = select_cols(songDF)
    songDF.head()



    def genre_preprocess(df):
        df['genres_list'] = df['genres'].apply(lambda x: " ".join(x) if isinstance(x, list) else x.split(" "));
        return df
    songDF = genre_preprocess(songDF)
    songDF['genres_list'].head()




    def playlist_preprocess(df):
        df = drop_duplicates(df)
        df = select_cols(df)
        df = genre_preprocess(df)
        return df




    def getSubjectivity(text):
       text = str(text)
       return TextBlob(text).sentiment.subjectivity

    def getPolarity(text):
       text = str(text)
       return TextBlob(text).sentiment.polarity

    def getAnalysis(score, task="polarity"):
        if task == "subjectivity":
            if score < 1/3: return "low";
            elif score > 1/3: return "high";
            else: return "medium";
        else:
            if score < 0: return 'Negative';
            elif score == 0:return 'Neutral';
            else: return 'Positive';

    def sentiment_analysis(df, text_col):
        df['subjectivity'] = df[text_col].apply(getSubjectivity).apply(lambda x: getAnalysis(x,"subjectivity"));
        df['polarity'] = df[text_col].apply(getPolarity).apply(getAnalysis);
        return df;



    sentiment = sentiment_analysis(songDF, "track_name")
    sentiment.head()


    def ohe_prep(df, column, new_name): 
        tf_df = pd.get_dummies(df[column])
        feature_names = tf_df.columns
        tf_df.columns = [new_name + "|" + str(i) for i in feature_names]
        tf_df.reset_index(drop = True, inplace = True)    
        return tf_df



    subject_ohe = ohe_prep(sentiment, 'subjectivity','subject')
    subject_ohe.iloc[0]



    tfidf = TfidfVectorizer()
    tfidf_matrix =  tfidf.fit_transform(songDF['genres_list'].apply(lambda x: " ".join(x)))
    genre_df = pd.DataFrame(tfidf_matrix.toarray())
    genre_df.columns = ['genre' + "|" + i for i in tfidf.get_feature_names_out()]
    if 'genre|unknown' in genre_df.columns:
        genre_df.drop(columns='genre|unknown')
    genre_df.reset_index(drop = True, inplace=True)
    genre_df.iloc[0]



    print(songDF['artist_pop'].describe())


    pop = songDF[["artist_pop"]].reset_index(drop = True)
    scaler = MinMaxScaler()
    pop_scaled = pd.DataFrame(scaler.fit_transform(pop), columns = pop.columns)
    pop_scaled.head()



    def create_feature_set(df, float_cols):

        tfidf = TfidfVectorizer()
        tfidf_matrix =  tfidf.fit_transform(df['genres_list'].apply(lambda x: " ".join(x)))
        genre_df = pd.DataFrame(tfidf_matrix.toarray())
        genre_df.columns = ['genre' + "|" + i for i in tfidf.get_feature_names_out()]
        if 'genre|unknown' in genre_df.columns:
            genre_df.drop(columns='genre|unknown') # drop unknown genre
        genre_df.reset_index(drop = True, inplace=True)

        df = sentiment_analysis(df, "track_name")

        subject_ohe = ohe_prep(df, 'subjectivity','subject') * 0.3
        polar_ohe = ohe_prep(df, 'polarity','polar') * 0.5
        key_ohe = ohe_prep(df, 'key','key') * 0.5
        mode_ohe = ohe_prep(df, 'mode','mode') * 0.5

        pop = df[["artist_pop","track_pop"]].reset_index(drop = True)
        scaler = MinMaxScaler()
        pop_scaled = pd.DataFrame(scaler.fit_transform(pop), columns = pop.columns) * 0.2 

        floats = df[float_cols].reset_index(drop = True)
        scaler = MinMaxScaler()
        floats_scaled = pd.DataFrame(scaler.fit_transform(floats), columns = floats.columns) * 0.2

        final = pd.concat([genre_df, floats_scaled, pop_scaled, subject_ohe, polar_ohe, key_ohe, mode_ohe], axis = 1)

        # Add song id
        final['id']=df['id'].values

        return final



    float_cols = songDF.dtypes[songDF.dtypes == 'float64'].index.values


    complete_feature_set = create_feature_set(songDF, float_cols=float_cols)


    ### This is the test data
    playlistDF_test = playlist_preprocess(playlistDF_test)
    playlistDF_test.head()


    def generate_playlist_feature(complete_feature_set, plist_df):

        complete_feature_set_playlist = complete_feature_set[complete_feature_set['id'].isin(plist_df['id'].values)]
        complete_feature_set_nonplaylist = complete_feature_set[~complete_feature_set['id'].isin(plist_df['id'].values)]
        complete_feature_set_playlist_final = complete_feature_set_playlist.drop(columns = "id")
        return complete_feature_set_playlist_final.sum(axis = 0), complete_feature_set_nonplaylist



    complete_feature_set_playlist_vector, complete_feature_set_nonplaylist = generate_playlist_feature(complete_feature_set, playlistDF_test)


    complete_feature_set_nonplaylist.head()



    complete_feature_set_playlist_vector



    def generate_playlist_recos(df, features, nonplaylist_features):
        non_playlist_df = df[df['id'].isin(nonplaylist_features['id'].values)]
        non_playlist_df['sim'] = cosine_similarity(nonplaylist_features.drop('id', axis = 1).values, features.values.reshape(1, -1))[:,0]
        non_playlist_df_top_40 = non_playlist_df.sort_values('sim',ascending = False).head(40)
        return non_playlist_df_top_40



    recommend = generate_playlist_recos(songDF, complete_feature_set_playlist_vector, complete_feature_set_nonplaylist)
    return recommend["name"]