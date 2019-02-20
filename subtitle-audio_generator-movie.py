import os
import glob
import numpy as np
import re
import moviepy.editor as mp
from bs4 import BeautifulSoup
from scipy.io import wavfile

source_path = '/home/manish/movie_data'
for i,movie in enumerate(os.listdir(source_path)):
    print('Currently doing movie number {0}. {1}'. format(i,movie))
    filepath = os.path.join(source_path,movie)

    subtitle_file = glob.glob(os.path.join(filepath,'*srt'))
    video_file = (glob.glob(os.path.join(filepath,'*.mkv')) or glob.glob(os.path.join(filepath,'*.mp4')) or
                 glob.glob(os.path.join(filepath, '*.avi')))
    audio_file = glob.glob(os.path.join(filepath,'*.wav'))
    source_flag = None
    html_flag = None

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


    elif audio_file:
        if len(audio_file)==1:
            audio_file=audio_file[0]
            source_flag = 'audio'
        else:
            print('More than 1 audio file present ,total present --> {}'.format(len(audio_file)))

    elif not audio_file and not video_file:
        print("Neither video or audio file present")

    if subtitle_file:
        if len(subtitle_file)==1:
            subtitle_file=subtitle_file[0]
        else:
            print('More than 1 subtitles present, total present --> {}'.format(len(subtitle_file)))
    else:
        print("No subtitles found for this.")

    with open(subtitle_file,'r') as f:
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

    for j,subtitle in enumerate(subtitles):
        print("Total subtitles text processed till now -->{0}/{1}".format(j,len(subtitles),end='\r'))
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

        if source_flag == 'video':
            ## for .mkv file:
            clip = mp.VideoFileClip(video_file).subclip(start_time,end_time)
            clip.audio.write_audiofile(output_path+'/'+sr_no+'_'+movie+'_'+str(start_raw.split(',')[0])+'--'+str(end_raw.split(',')[0])+'.wav')

        if source_flag == 'audio':
            ## for .wav present:
            clip = mp.AudioFileClip(audio_file).subclip(start_time,end_time)
            clip.write_audiofile(output_path+'/'+sr_no+'_'+movie+'_'+str(start_raw.split(',')[0])+'--'+str(end_raw.split(',')[0])+'.wav')
