import os, sys, random, subprocess, re, math

def Generate(video=False):
	letters = [chr(i) for i in range(ord('a'),ord('a')+26)]

	# Possible directories to gather sounds from.
	# Can be used to separate HL1 sounds from HL2 sounds.
	# WARNING make sure to have a "music" folder in all of the specified folders..
	possible_dirs = ["H:/GCFScape extract/HL2/sound/", "H:/GCFScape extract/valve/sound/"]

	video_dir = "./video/"

	# This is the sound directory. Will be crawled recursively.
	walk_dir = random.choice(possible_dirs)

	print('walk_dir = ' + walk_dir)

	# List of gathered sound files
	sfx_files = []

	for root, subdirs, files in os.walk(walk_dir):

		for filename in files:
			file_path = os.path.join(root, filename)

			# Exclude any music and sfk files (sfk is a special extension used by Vegas)
			if not any(x in file_path for x in ('.sfk', 'music')):
				sfx_files.append(file_path)

				#print('\t- file %s (full path: %s)' % (filename, file_path))

	print('found %i files' % len(sfx_files))

	# If the video wasn't specified
	if video == False:
		vids = os.listdir(video_dir)
		video = "{}{}".format(video_dir, random.choice(vids))

	print("Chosen video: {}".format(video))

	songs = os.listdir("{}music/".format(walk_dir))
	song = "{}music/{}".format(walk_dir, random.choice(songs))
	print("Chosen song:  {}".format(song))

	# Remove the file, so:
	# If an error comes up, it doesn't post the
	# last output file, instead stops and shows
	# an error
	if os.path.isfile("out.mp4"):
		os.remove("out.mp4")


	# This part is a little confusing,
	# but it just gathers the length of
	# the video and music using ffprobe

	lengthRegex = r'Duration: ([0-9]+):([0-9]+):([0-9]+).[0-9]+'

	vidLength = 0
	vidLengthStr = getLength(video)[0] # is an array
	vidLengthSearch = re.search(lengthRegex, vidLengthStr, re.IGNORECASE)

	songLength = 0
	songLengthStr = getLength(song)[0] # is an array
	songLengthSearch = re.search(lengthRegex, songLengthStr, re.IGNORECASE)

	if vidLengthSearch:
		tempLength = [int(vidLengthSearch.group(1)), int(vidLengthSearch.group(2)), int(vidLengthSearch.group(3))]
		print("Video length: {}".format(tempLength))
		vidLength = tempLength[0] * 3600 + tempLength[1] * 60 + tempLength[2]

		tempLength = [int(songLengthSearch.group(1)), int(songLengthSearch.group(2)), int(songLengthSearch.group(3))]
		print("Song length: {}".format(tempLength))
		songLength = tempLength[0] * 3600 + tempLength[1] * 60 + tempLength[2]

	print("")
	print("Converted video length: {} seconds".format(str(vidLength)))
	print("Converted song length:  {} seconds".format(str(songLength)))

	startTime = 0

	     #10 sec      #6 sec
	if songLength > vidLength:
		sub = songLength - vidLength
		startTime = random.randint(0, sub)

		# sub = 10 - 6 = 4 sec
		# 0 - 4 should be randomized

	videoName = video.replace("sound_", "")
	songName = song

	sfx_amount = math.floor(vidLength / 1.5)
	if sfx_amount > len(letters)-2:
		sfx_amount = len(letters)-2

	print("SFX AMOUNT: {}".format(sfx_amount))

	input_sfx = random.sample(sfx_files, sfx_amount)
	inputs = ""
	filters = ""

	# list of input audio for the ffmpeg command line
	for i in input_sfx:
		inputs += "-i \"{}\" ".format(i)
		
	print(inputs)

	# complex filter attributes
	count = 1
	
	for i in input_sfx:
		count += 1
		random_delay = random.randint(0, vidLength * 1000)
		filters += "[{}]adelay={}|{}[{}];".format(count, random_delay, random_delay, letters[count-1])

	count = 1

	filters += "[1]" # Background music

	for i in input_sfx:
		count += 1
		filters += "[{}]".format(letters[count-1])

	filters += "amix={}:duration=longest".format(len(input_sfx)+1)

	print(filters)

	print()
	print('ffmpeg -i \"{}\" -ss {} -i \"{}\" {} -map 0:v:0 -map 1:a:0 -c:v libx264 -filter_complex \"{}\" -t {} -y out.mp4'.format(video, startTime, song, inputs, filters, secToStamp(vidLength)))

	os.system('ffmpeg -i \"{}\" -ss {} -i \"{}\" {} -map 0:v:0 -map 1:a:0 -c:v libx264 -filter_complex \"{}\" -t {} -y out.mp4'.format(video, startTime, song, inputs, filters, secToStamp(vidLength)))

	return (videoName, songName, secToStamp(startTime), input_sfx)

def getLength(filename):
	#filename = "\"{}\"".format(filename)
	result = subprocess.Popen(["ffprobe", filename],
		stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
	return [x.decode('utf-8') for x in result.stdout.readlines() if "Duration" in x.decode('utf-8')]

def secToStamp(secs):
	minutes = math.floor(secs / 60)
	seconds = secs % 60

	if minutes < 10:
		minutes = "0" + str(minutes)

	if seconds < 10:
		seconds = "0" + str(seconds)

	return "{}:{}".format(minutes, seconds)

#Generate()