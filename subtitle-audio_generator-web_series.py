from scipy.io import wavfile
import os
import glob
import numpy as np
import re
import moviepy.editor as mp
from bs4 import BeautifulSoup
import subprocess

source_path = '/home/manish/movie_data'
## Pre-processing for F.R.I.E.N.D.S. :
## output of this will be, for every season, there will be an episode directory consisting of
## the subtitle file and the episode video.
series_name = 'Friends'
seasons = glob.glob(os.path.join(source_path,series_name+'*'))
for i,season in enumerate(seasons):
    # print(i, '\t', season)
    try:
        os.rename(season,re.findall(r'(.*) Complete 720p',season)[0].replace(' ','_'))
        ## replacing white spaces with underscores
        # os.rename(season,season.replace(' ','_'))
    except:
        print('Filename already changed')
        
## This block of code re-arranges the all the directories such that, for every season, and for every episode,
## the video file and subtitle file are in a single directory together.
seasons = glob.glob(os.path.join(source_path,series_name+'*'))
for i,season in enumerate(seasons):
    # print(i, '\t', season)
    subtitle_file_season = os.path.join(season,'subtitles')
    for j,episodes in enumerate(glob.glob(os.path.join(season,'*.mkv'))):
        # print(j, '\t', episodes)
        ep_video = os.path.basename(episodes)
        ep_name = re.findall(r'friends[._](.*)[._]720p',ep_video)[0]
        ep_name = ep_name.lower()
        subtitle_name = [x for x in glob.glob(os.path.join(subtitle_file_season,'*.srt')) if re.findall('friends.'+ep_name+'.720p..*',x.lower())][0]
        subtitle_fname = os.path.basename(subtitle_name)
        os.mkdir(os.path.join(season,ep_name))
        os.rename(episodes,os.path.join(season,ep_name+'/'+ep_video))
        os.rename(subtitle_name,os.path.join(season,ep_name+'/'+subtitle_fname))
    os.rmdir(subtitle_file_season)
    
##########################################



#### with ffmpeg
for i,season in enumerate(seasons):
    print('Currently doing season number {0}. {1}'.format(i,os.path.basename(season)))
    orig_filepath = os.path.join(source_path,season)
    episode_folders = [os.path.join(source_path,season,x) for x in os.listdir(os.path.join(source_path,season)) if os.path.isdir(os.path.join(source_path,season,x))]
    # episode_folders = os.walk(os.path.join(source_path,season)).__next__()[1]
    for j,episode in enumerate(episode_folders):
        print('Currently doing episode number {0}. {1}'.format(j,os.path.basename(episode)))
        filepath = os.path.join(orig_filepath,episode)
        subtitle_file = glob.glob(os.path.join(filepath,'*srt'))
        video_file = (glob.glob(os.path.join(filepath,'*.mkv')) or glob.glob(os.path.join(filepath,'*.mp4')) or 
                     glob.glob(os.path.join(filepath,'*.avi')))
        audio_file = glob.glob(os.path.join(filepath,'*.wav'))
        source_flag = None
        html_flag = None
        multiple_sources = None

        ## creating the directory to dump in the outputs
        if not os.path.exists(os.path.join(filepath,'output')):
            os.mkdir(os.path.join(filepath,'output'))
        else:    
            print("Directory \'output\' already exists")

        output_path = os.path.join(filepath,'output')

        if video_file:
            if len(video_file)==1:
                video_file=video_file[0]
                source_flag = 'video'
            else:
                print('More than 1 video file present ,total present --> {}'.format(len(video_file)))
                multiple_sources = True


        elif audio_file:
            if len(audio_file)==1:
                audio_file=audio_file[0]
                source_flag = 'audio'
            else:
                print('More than 1 audio file present ,total present --> {}'.format(len(audio_file)))
                multiple_sources = True

        elif not audio_file and not video_file:
            print("Neither video or audio file present")

        if subtitle_file:
            if len(subtitle_file)==1:
                subtitle_file=subtitle_file[0]
            else:
                print('More than 1 subtitles present, total present --> {}'.format(len(subtitle_file)))
                try:
                    assert multiple_sources
                except:
                    print("Just 1 audio/video source for the multiple subtitles files")
        else:
            print("No subtitles found for this.")


        ## convert video to audio
        output_audio_file = os.path.join(filepath,re.findall(r'(.*).mkv',os.path.basename(video_file))[0]+'.wav')
        command = "ffmpeg -i " +video_file+" -ab 160k -ac 2 -ar 44100 -vn "+output_audio_file
        subprocess.call(command, shell=True)

        with open(subtitle_file,'r',errors='ignore') as f:
            orig = f.readlines()

        subtitles = []
        time_frame = []
        for o in orig:
            time_frame.append(o)
            if o == '\n':
                subtitles.append(time_frame)
                time_frame = []
        if time_frame:
            subtitles.append(time_frame)
            time_frame = []

        final_list=[]
        columns = ['Sr_No','Start_time','End_time','Text']

        ep = os.path.basename(episode)
        for j,subtitle in enumerate(subtitles):
            print("Total subtitles text processed till now -->{0}/{1}".format(j,len(subtitles)),end = '\r')
            #### For the subtitles extracting text, and the start and end time ####
            ## to check for valid subtitle block
            try:
                assert subtitle[0].strip('\n').isdigit()
                sr_no = subtitle[0].strip('\n')
            except:
                try:
                    assert re.search(r'\d+',subtitle[0])
                    sr_no = re.findall(r'\d+',subtitle[0])[0]
                except:
                    print('Block has no serial number')
                    break



            start_raw, end_raw = subtitle[1].split('-->')
            start_raw = start_raw.strip()
            end_raw = end_raw.strip()

            hh1,mm1,ssss1 = start_raw.split(':')
            ss1,ms1 = ssss1.split(',')

            hh2,mm2,ssss2 = end_raw.split(':')
            ss2,ms2 = ssss2.split(',')

            start_time = int(hh1)*3600 + int(mm1)*60 + int(ss1) + (int(ms1)/1000)
            end_time = int(hh2)*3600 + int(mm2)*60 + int(ss2) + (int(ms2)/1000)


            raw_text = ''.join(subtitle[2:-1]).replace('\n',' ').strip()
            html_flag = (('<font' in raw_text) or ('</font>' in raw_text) or
                        ('<i' in raw_text) or ('</i>' in raw_text))

            if html_flag:
                sub_text = BeautifulSoup(raw_text,'html.parser').get_text().strip('\n')
                # re.findall(r'<.*>(.*)<.*>\n',subtitle[2])

            else:
                sub_text = raw_text


            single_row = [sr_no, start_time, end_time, sub_text]
            final_list.append(single_row)
            with open(output_path+'.txt','a') as f:
                f.write(sr_no+'\t'+sub_text)
                f.write('\n')


            ## clips audio between start_time and end_time
            final_op = output_path+'/'+sr_no+'_'+ep+'_'+str(start_raw.split(',')[0])+'--'+str(end_raw.split(',')[0])+'.wav'
            command2 = "ffmpeg -i "+output_audio_file+" -ss "+str(start_time)+" -to "+str(end_time)+" -c copy "+final_op
            subprocess.call(command2, shell=True)
