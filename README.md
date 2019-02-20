# Subtitle-Audio_Generator

This particular use case is for extracting the audio from a movie, and splitting the audio in order to map every audio file to its corresponding subtitle. The data required for the script is either the entire movie video ( in .mkv, .avi or .mp4 formats) or the audio format as well, and a subtitle file (.srt file format). The subtitle files are also pre-processed, and divided into individual subtitles, extracting the test within, as well as the time duration when it was spoken in the movie. 

The main aim for this application is to prepare a dataset of movie audios, having the audio partitions as the individual data points, and with the associated subtitle as its label/tag. 

There are a total of 2 scripts:- <br />
1. The first script is targetted for movies, having subtitles and the film for just that 1 movie. <br />
2. The second script is targetted for web series, which can have multiple seasons, and each season has multiple episodes.
