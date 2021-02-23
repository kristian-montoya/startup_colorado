import os
import csv
import math
import shutil
import pdfkit
import pandas as pd
from os import listdir
from os.path import isfile, join


#======================================
# CLASSES 
#======================================
class Directory:
	def __init__(self):
		self.users = []
		self.groups = []
		self.group_names = {}
		self.categories = {}
		self.categories['groups'] = []
		self.categories['expertise'] = []
		self.categories['industry'] = []
		self.categories['interests'] = []
		self.categories['resources'] = []
		self.categories['stages'] = []
		self.categories['member_types'] = []
		self.current_date = ''


class User:
	def __init__(self, uid, first_name, last_name, email, last_active, created, count, score, groups, expertise, industry, interests, resources, location, stages, active, member_types):
		self.uid = uid #[STRING]   user id
		self.first_name = first_name #tracks name of play
		self.last_name = last_name
		self.email = email
		self.last_active = last_active #date profile was last active
		self.created = created #date profile was created
		self.count = int(count) # [INT]   number of times signed in
		self.score = int(score) # [INT]
		self.categories = {}
		self.categories['groups'] = groups
		self.categories['expertise'] = expertise
		self.categories['industry'] = industry
		self.categories['interests'] = interests
		self.categories['resources'] = resources
		self.categories['stages'] = stages
		self.categories['member_types'] = member_types
		self.location = location
		self.active = active
		

class Group:
	def __init__(self, gid, name):
		self.gid = gid
		self.name = name
		self.members = []


#======================================
# HELPER FUNCTIONS
#======================================
def get_max_string_len(data):
	value = 0
	for item in data:
		if len(item) > value:
			value = len(item)
	return value


def get_group(directory, gid):
	value = None
	for group in directory.groups:
		if group.gid == gid:
			value = group
			break
	return value


def get_index(categories, category):
	index = ""
	if category in categories:
		index = categories.index(category)

	return index


def add_group_member(directory, user, gid):
	gid = int(gid)
	group = get_group(directory, gid)
	if group == None:
		group = Group(gid, directory.group_names[gid])
		directory.groups.append(group)
	group.members.append(user)


def fix_list(data):
	result = []

	for item in data:
		if type(item) == str:
			if len(item) > 0:
				if item[0] == ' ':
					item = item[1:]
		if item != '':
			result.append(item)

	return result


def format_date(date):
	date = date.split('-')
	date = date[1]+'/'+date[2]+'/'+date[0]
	return date


def split_dict(full_dict, num):

	dicts = []
	keys = list(full_dict.keys())
	items = list(full_dict.values())
	# print(len(keys))

	full = len(keys)

	status = 0

	for i in range(num):
		sub_dict = {}

		length = 0
		if i == num-1:
			if num == 3:
				length = full - (math.ceil(full/3) * 2)
			else:
				length = full - math.ceil(full/2)
		else:
			length = math.ceil(full/num)

		for j in range(status,length+status):
			if j >= full:
				break
			# print(j)
			sub_dict[keys[j]] = items[j]

		status += length
		dicts.append(sub_dict)
		
	return dicts


def most_recent_date(d1, d2):

	d1 = d1.split("-")
	d2 = d2.split("-")

	new = d1
	old = d2


	#newer year
	if int(d2[0]) > int(d1[0]):
		new = d2
		old = d1

	#same year
	elif int(d2[0]) == int(d1[0]):

		#newer month
		if int(d2[1]) > int(d1[1]):
			new = d2
			old = d1

		#same month
		elif int(d2[1]) == int(d1[1]):

			#newer day
			if int(d2[2]) >= int(d1[2]):
				new = d2
				old = d1

	new = new[0]+'-'+new[1]+'-'+new[2]
	old = old[0]+'-'+old[1]+'-'+old[2]

	return new, old


#======================================
# PRIMARY FUNCTIONS
#======================================
def get_dates(path):

	value = ""

	files = [f for f in listdir(path) if isfile(join(path, f))]
	dates = []

	for file in files:
		if "User_export_" in file:
			date = file.replace("~$","")
			date = date.replace("User_export_","")
			date = date.replace(".xlsx","")
			if date not in dates:
				dates.append(date)

	done = False

	while not done:
		previous = dates.copy()

		for i in range(len(dates)):
			if i == len(dates) - 1:
				break

			new, old = most_recent_date(dates[i], dates[i+1])
			dates[i] = new
			dates[i+1] = old

		if dates == previous:
			done = True

	return dates


def read_group_names(path):
	names = {}
	file_name = path + "names.csv"
	with open(file_name) as file:
		data = csv.reader(file, delimiter=",")
		for row in data:
			gid = int(row[0])
			name = row[1]

			names[gid] = name

	return names


def fill_directory(directory, category, data):
	filtered_data = []
	for item in data:
		if item == 'Outoor Recreation':
			item = 'Outdoor Recreation'
		if item not in directory.categories[category]:
			directory.categories[category].append(item)
		if item not in filtered_data:
			filtered_data.append(item)
	return filtered_data


def read_users(path, directory):
	users = []

	df = pd.read_excel(path)
	df = df.fillna("")

	categories = list(df.columns)

	data = df.to_numpy()

	fields = [
		"ID",
		"First name",
		"Last name",
		"Email",
		"Last sign in date",
		"Created at",
		"Count of sign in",
		"Engagement Scoring:Current score",
		"Groups Member:Group Member",
		"_281d4ac7_Expertise",
		"_07417723_Industry_1",
		"_ec0c314f_Resources_I_Am_Interested_In",
		"_e63e1ef3_Resources",
		"_0318eefd_Business_Stage",
		"SubNetworks:Title",
		"Live Location:Address",
		"Live Location:City"
	]

	lists = [
		"Groups Member:Group Member",
		"_281d4ac7_Expertise",
		"_07417723_Industry_1",
		"_ec0c314f_Resources_I_Am_Interested_In",
		"_e63e1ef3_Resources",
		"_0318eefd_Business_Stage",
		"SubNetworks:Title"
	]

	for row in data:
		info = []

		user_data = {
			"uid": "",
			"first_name": "",
			"last_name": "",
			"email": "",
			"last_active": "",
			"created": "",
			"count": "0",
			"score": "0",
			"groups": [],
			"expertise": [],
			"industry": [],
			"interests": [],
			"resources": [],
			"stages": [],
			"member_types": [],
			"full_address": "",
			"city": "",
		}

		list_categories = ["groups","expertise","industry","interests","resources","stages","member_types"]

		keys = list(user_data.keys())
		for i in range(len(fields)):
			field = fields[i]
			index = get_index(categories, field)
			entry = user_data[keys[i]]

			if index != "":

				if row[index] != "":

					if (field == "Last sign in date") or (field == "Created at"):
						entry = row[index].split(' ')[0]

					elif field in lists:
						fixed_list = fix_list(row[index].split(","))
						if (field == "SubNetworks:Title") and ("Undefined" in fixed_list):
							fixed_list.remove("Undefined")
						entry = fill_directory(directory, list_categories.pop(0), fixed_list)

					else:
						entry = row[index]

			user_data[keys[i]] = entry

		active = False
		if int(user_data["count"]) > 0:
			active = True


		location = "NO RECORDED LOCATION"

		city = user_data["city"]
		full_address = user_data["full_address"]
		if len(city) != 0:
			location = city
		else:
			if len(full_address) != 0:
				split = full_address.split(",")
				if len(split) > 3:
					location = split[1]
				else:
					location = split[0]

		user_data["active"] = active
		user_data["location"] = location

		user = User(
			user_data["uid"],
			user_data["first_name"],
			user_data["last_name"],
			user_data["email"],
			user_data["last_active"],
			user_data["created"],
			user_data["count"],
			user_data["score"],
			user_data["groups"],
			user_data["expertise"],
			user_data["industry"],
			user_data["interests"],
			user_data["resources"],
			user_data["location"],
			user_data["stages"],
			user_data["active"],
			user_data["member_types"]
		)
		users.append(user)

		for gid in user_data["groups"]:
			add_group_member(directory, user, gid)

	return users


def generate_pdf(name, path):
	options = {
		'page-size': 'A4',
		'margin-top': '0in',
		'margin-right': '0in',
		'margin-bottom': '0in',
		'margin-left': '0in',
		'quiet': '',
		}

	group = ''.join([i for i in name if not i.isdigit()])
	if group[0] == '_':
		group = group[1:]
	group = group.replace("_",' ')

	print("Generating " + group + " report...")
	output = path + name + ".pdf"
	pdfkit.from_file('./html_report.html', output, options) 


def generate_group_pdf(curr_directory, prev_directory, group_dicts, diff_group_dict):

	original_template = ""

	with open('./data/html_template_group.csv', newline='') as csvfile:
		file = csv.reader(csvfile)
		for row in file:
			for item in row:
				original_template += item


	for group in curr_directory.groups:

		template = original_template
		gid = group.gid
		name = group.name

		date = curr_directory.current_date
		
		prev_group = get_group(prev_directory, gid)
		if prev_group != None:
			date += '<br>Previous Report Date: ' + prev_directory.current_date

		size_diff = None
		if prev_directory != None:
			if prev_group != None:
				size_diff = len(group.members) - len(prev_group.members)

		size = str(len(group.members))
		if size_diff != None:
			if size_diff > 0:
				size += '   (+'+str(size_diff)+')'
			elif size_diff < 0:
				size += '   ('+str(size_diff)+')'


		path = "./data/group_data/cover_photos/"
		files = [f for f in listdir(path) if isfile(join(path, f))]
		background_name = "default.jpg"
		# for file in files:
		# 	if str(gid) in file:
		# 		background_name = file
		background = path + background_name

		path = "./data/group_data/logos/"
		files = [f for f in listdir(path) if isfile(join(path, f))]
		logo_name = "default.jpg"
		# for file in files:
		# 	if str(gid) in file:
		# 		logo_name = file
		logo = path + logo_name
		
		categories = ['locations','industries','expertises','interests','stages','member_types']
		group_dict = group_dicts[gid]
		text_dict = {}

		for category in categories:
			sub_dict = group_dict[category]

			#single col tables
			if (category == "stages") or (category == "member_types"):
				text = ''
				for item in sub_dict:
					text += '<tr><td>'+item+'</td>'
					text += '<td class="count">'+str(sub_dict[item])

					if diff_group_dict != None:
						diff = diff_group_dict[gid][category][item]
						if diff < 0:
							text += ' ('+str(diff)+')'
						elif diff > 0:
							text += ' (+'+str(diff)+')'

					text += '</td></tr>'

				text_dict[category] = text

			#double col tables
			else:
				if category == "locations":
					num = 4
				else:
					num = 2
				dicts = split_dict(sub_dict, num)
				for i in range(len(dicts)):
					text = ''
					new_sub_dict = dicts[i]
					for item in new_sub_dict:
						text += '<tr><td>'+item+'</td>'
						text += '<td class="count">'+str(new_sub_dict[item])

						if diff_group_dict != None:
							diff = diff_group_dict[gid][category][item]
							if diff < 0:
								text += ' ('+str(diff)+')'
							elif diff > 0:
								text += ' (+'+str(diff)+')'

						text += '</td></tr>'

					cat = category+"_"+str(i+1)

					text_dict[cat] = text


		template = template.replace('[INSERT GROUP BACKGROUND]', background)
		template = template.replace('[INSERT GROUP LOGO]', logo)
		template = template.replace('[INSERT GROUP TITLE]', name)
		template = template.replace('[INSERT STAGE ENTRIES]', text_dict['stages'])
		template = template.replace('[INSERT MEMBER TYPE ENTRIES]', text_dict['member_types'])
		template = template.replace('[INSERT INTEREST 1 ENTRIES]', text_dict['interests_1'])
		template = template.replace('[INSERT INTEREST 2 ENTRIES]', text_dict['interests_2'])
		template = template.replace('[INSERT LOCATION 1 ENTRIES]', text_dict['locations_1'])
		template = template.replace('[INSERT LOCATION 2 ENTRIES]', text_dict['locations_2'])
		template = template.replace('[INSERT LOCATION 3 ENTRIES]', text_dict['locations_3'])
		template = template.replace('[INSERT LOCATION 4 ENTRIES]', text_dict['locations_4'])
		template = template.replace('[INSERT EXPERTISE 1 ENTRIES]', text_dict['expertises_1'])
		template = template.replace('[INSERT EXPERTISE 2 ENTRIES]', text_dict['expertises_2'])
		template = template.replace('[INSERT INDUSTRY 1 ENTRIES]', text_dict['industries_1'])
		template = template.replace('[INSERT INDUSTRY 2 ENTRIES]', text_dict['industries_2'])
		template = template.replace('[INSERT NUM USERS]', size)
		template = template.replace('[INSERT DATE]', date)


		html = open("./html_report.html","w")
		html.write(template)
		html.close()

		file_name = name.replace(' ','_')
		file_name = str(gid) + '_' + file_name

		path = './reports/group_reports/'
		generate_pdf(file_name, path)

		if os.path.exists("./html_report.html"):
			os.remove("./html_report.html")


def generate_sum_pdf(curr_directory, prev_directory, sum_dict, diff_sum_dict):

	template = ""

	with open('./data/html_template_sum.csv', newline='') as csvfile:
		file = csv.reader(csvfile)
		for row in file:
			for item in row:
				template += item


	name = "User Sum Report"
	background = "./data/group_data/cover_photos/default.jpg"
	logo = "./data/group_data/logos/default.jpg"


	date = curr_directory.current_date
	if prev_directory != None:
		date += '<br>Previous Report Date: ' + prev_directory.current_date

	size_diff = None
	if prev_directory != None:
		size_diff = len(curr_directory.users) - len(prev_directory.users)

	size = str(len(curr_directory.users))
	if size_diff != None:
		if size_diff > 0:
			size += '   (+'+str(size_diff)+')'
		elif size_diff < 0:
			size += '   ('+str(size_diff)+')'

	
	categories = ['locations','industries','expertises','interests','stages','member_types']
	text_dict = {}

	for category in categories:
		sub_dict = sum_dict[category]

		#single col tables
		if (category == "stages") or (category == "member_types"):
			text = ''
			for item in sub_dict:
				text += '<tr><td>'+item+'</td>'
				text += '<td class="count">'+str(sub_dict[item])

				if diff_sum_dict != None:
					diff = diff_sum_dict[category][item]
					if diff < 0:
						text += ' ('+str(diff)+')'
					elif diff > 0:
						text += ' (+'+str(diff)+')'

				text += '</td></tr>'

			text_dict[category] = text

		#double col tables
		else:
			if category == "locations":
				num = 4
			else:
				num = 2
			dicts = split_dict(sub_dict, num)
			for i in range(len(dicts)):
				text = ''
				new_sub_dict = dicts[i]
				for item in new_sub_dict:
					text += '<tr><td>'+item+'</td>'
					text += '<td class="count">'+str(new_sub_dict[item])

					if diff_sum_dict != None:
						diff = diff_sum_dict[category][item]
						if diff < 0:
							text += ' ('+str(diff)+')'
						elif diff > 0:
							text += ' (+'+str(diff)+')'

					text += '</td></tr>'

				cat = category+"_"+str(i+1)

				text_dict[cat] = text


	template = template.replace('[INSERT GROUP BACKGROUND]', background)
	template = template.replace('[INSERT GROUP LOGO]', logo)
	template = template.replace('[INSERT GROUP TITLE]', name)
	template = template.replace('[INSERT STAGE ENTRIES]', text_dict['stages'])
	template = template.replace('[INSERT MEMBER TYPE ENTRIES]', text_dict['member_types'])
	template = template.replace('[INSERT INTEREST 1 ENTRIES]', text_dict['interests_1'])
	template = template.replace('[INSERT INTEREST 2 ENTRIES]', text_dict['interests_2'])
	template = template.replace('[INSERT LOCATION 1 ENTRIES]', text_dict['locations_1'])
	template = template.replace('[INSERT LOCATION 2 ENTRIES]', text_dict['locations_2'])
	template = template.replace('[INSERT LOCATION 3 ENTRIES]', text_dict['locations_3'])
	template = template.replace('[INSERT LOCATION 4 ENTRIES]', text_dict['locations_4'])
	template = template.replace('[INSERT EXPERTISE 1 ENTRIES]', text_dict['expertises_1'])
	template = template.replace('[INSERT EXPERTISE 2 ENTRIES]', text_dict['expertises_2'])
	template = template.replace('[INSERT INDUSTRY 1 ENTRIES]', text_dict['industries_1'])
	template = template.replace('[INSERT INDUSTRY 2 ENTRIES]', text_dict['industries_2'])
	template = template.replace('[INSERT NUM USERS]', size)
	template = template.replace('[INSERT DATE]', date)



	html = open("./html_report.html","w")
	html.write(template)
	html.close()

	file_name = name.replace(' ','_')
	path = './reports/'
	generate_pdf(file_name, path)

	if os.path.exists("./html_report.html"):
		os.remove("./html_report.html")


def fetch_directories():
	export_dir_name = "./data/user_exports/"
	dates = get_dates(export_dir_name)

	curr_date = dates[0]
	prev_date = None
	if len(dates) > 1:
		prev_date = dates[1]

	curr_date = format_date(curr_date)

	export_name = "User_export_" + dates[0] + ".xlsx"
	export_path = export_dir_name + export_name
	group_dir_name = "./data/group_data/"



	curr_directory = Directory()
	curr_directory.current_date = curr_date
	curr_directory.group_names = read_group_names(group_dir_name)
	curr_directory.users = read_users(export_path, curr_directory)
	curr_directory.users.sort(key=lambda user:user.score, reverse=True)


	prev_directory = None

	if prev_date != None:
		prev_date = format_date(prev_date)
		export_name = "User_export_" + dates[1] + ".xlsx"
		export_path = export_dir_name + export_name

		prev_directory = Directory()
		prev_directory.current_date = prev_date
		prev_directory.group_names = read_group_names(group_dir_name)
		prev_directory.users = read_users(export_path, prev_directory)
		prev_directory.users.sort(key=lambda user:user.score, reverse=True)


	return curr_directory, prev_directory


#======================================
# DICTIONARY HANDLER FUNCTIONS
#======================================
def create_diff_group_dict(curr_group_directory, prev_group_directory):

	diff_group_dict = {}

	for gid in curr_group_directory.keys():
		diff_group_dict[gid] = {}
		for category in curr_group_directory[gid].keys():
			category_dict = {}
			for item in curr_group_directory[gid][category].keys():
				diff = 0
				if gid in prev_group_directory:
					if item in prev_group_directory[gid][category]:
						diff = curr_group_directory[gid][category][item] - prev_group_directory[gid][category][item]
					else:
						diff = curr_group_directory[gid][category][item]

				category_dict[item] = diff
			diff_group_dict[gid][category] = category_dict

	return diff_group_dict
		

def create_diff_sum_dict(curr_sum_directory, prev_sum_directory):

	diff_sum_dict = {}

	for category in curr_sum_directory.keys():
		category_dict = {}
		for item in curr_sum_directory[category].keys():
			diff = 0
			if item in prev_sum_directory[category]:
				diff = curr_sum_directory[category][item] - prev_sum_directory[category][item]
			else:
				diff = curr_sum_directory[category][item]

			category_dict[item] = diff
		diff_sum_dict[category] = category_dict

	return diff_sum_dict


#Creates and returns a dictionary that holds all groups and the selected demographics of each group
def create_group_dicts(directory):
	
	#create pie chart of composition of each group and the specified areas of interest (locations, industries, etc)
	
	
	#NOTE: Stages (the stage a user is in within their career) is NOT an accurate report. 
	#Not all users, only a select few in fact, have filled this information out.
	#In act, a single user may make up for 4 or 5 different reported stages; keep this in mind
	
	group_dict = {}
	for group in directory.groups:
		
		group_dict[group.gid] = {}
		locations = {}
		industries = {}
		expertises = {}
		interests = {}
		resources = {}
		stages = {}
		member_types = {}

		for user in group.members:

			if user.active:
			
				location = user.location.split(",")[0]
				if location not in locations:
					locations[location] = 1
				else:
					locations[location] += 1
					
				for industry in user.categories['industry']:
					if industry not in industries:
						industries[industry] = 1
					else:
						industries[industry] += 1
				
				for expertise in user.categories['expertise']:
					if expertise not in expertises:
						expertises[expertise] = 1
					else:
						expertises[expertise] += 1

				for interest in user.categories['interests']:
					if interest not in interests:
						interests[interest] = 1
					else:
						interests[interest] += 1
				
				for resource in user.categories['resources']:
					if resource not in resources:
						resources[resource] = 1
					else:
						resources[resource] += 1
				
				for stage in user.categories['stages']:
					if stage not in stages:
						stages[stage] = 1
					else:
						stages[stage] += 1 

				for member_type in user.categories['member_types']:
					if member_type not in member_types:
						member_types[member_type] = 1
					else:
						member_types[member_type] += 1 
					
		group_dict[group.gid]["locations"] = dict(sorted(locations.items(), key=lambda item:item[1], reverse=True))
		group_dict[group.gid]["industries"] = dict(sorted(industries.items(), key=lambda item:item[1], reverse=True))
		group_dict[group.gid]["expertises"] = dict(sorted(expertises.items(), key=lambda item:item[1], reverse=True))
		group_dict[group.gid]["interests"] = dict(sorted(interests.items(), key=lambda item:item[1], reverse=True))
		group_dict[group.gid]["resources"] = dict(sorted(resources.items(), key=lambda item:item[1], reverse=True))
		group_dict[group.gid]["stages"] = dict(sorted(stages.items(), key=lambda item:item[1], reverse=True))
		group_dict[group.gid]["member_types"] = dict(sorted(member_types.items(), key=lambda item:item[1], reverse=True))

	return group_dict


#Creates and returns a dictionary that holds all groups and the selected demographics of each group
def create_sum_dict(directory):
	
	#create pie chart of composition of each group and the specified areas of interest (locations, industries, etc)
	
	
	#NOTE: Stages (the stage a user is in within their career) is NOT an accurate report. 
	#Not all users, only a select few in fact, have filled this information out.
	#In act, a single user may make up for 4 or 5 different reported stages; keep this in mind
	

	sum_dict = {}

	locations = {}
	industries = {}
	expertises = {}
	interests = {}
	resources = {}
	stages = {}
	member_types = {}

	for user in directory.users:

		if user.active:
		
			location = user.location.split(",")[0]
			if location not in locations:
				locations[location] = 1
			else:
				locations[location] += 1
				
			for industry in user.categories['industry']:
				if industry not in industries:
					industries[industry] = 1
				else:
					industries[industry] += 1
			
			for expertise in user.categories['expertise']:
				if expertise not in expertises:
					expertises[expertise] = 1
				else:
					expertises[expertise] += 1

			for interest in user.categories['interests']:
				if interest not in interests:
					interests[interest] = 1
				else:
					interests[interest] += 1
			
			for resource in user.categories['resources']:
				if resource not in resources:
					resources[resource] = 1
				else:
					resources[resource] += 1
			
			for stage in user.categories['stages']:
				if stage not in stages:
					stages[stage] = 1
				else:
					stages[stage] += 1 

			for member_type in user.categories['member_types']:
				if member_type not in member_types:
					member_types[member_type] = 1
				else:
					member_types[member_type] += 1 
				
	sum_dict["locations"] = dict(sorted(locations.items(), key=lambda item:item[1], reverse=True))
	sum_dict["industries"] = dict(sorted(industries.items(), key=lambda item:item[1], reverse=True))
	sum_dict["expertises"] = dict(sorted(expertises.items(), key=lambda item:item[1], reverse=True))
	sum_dict["interests"] = dict(sorted(interests.items(), key=lambda item:item[1], reverse=True))
	sum_dict["resources"] = dict(sorted(resources.items(), key=lambda item:item[1], reverse=True))
	sum_dict["stages"] = dict(sorted(stages.items(), key=lambda item:item[1], reverse=True))
	sum_dict["member_types"] = dict(sorted(member_types.items(), key=lambda item:item[1], reverse=True))


	return sum_dict


def fetch_dicts(directory):

	sum_dict = None
	group_dict = None

	if directory != None:
		sum_dict = create_sum_dict(directory)
		group_dict = create_group_dicts(directory)

	return sum_dict, group_dict


def fetch_diff_dicts(curr_group_dict, curr_sum_dict, prev_group_dict, prev_sum_dict):
	diff_sum_dict = None
	diff_group_dict = None

	if prev_sum_dict != None and prev_group_dict != None:
		diff_group_dict = create_diff_group_dict(curr_group_dict, prev_group_dict)
		diff_sum_dict = create_diff_sum_dict(curr_sum_dict, prev_sum_dict)

	return diff_sum_dict, diff_group_dict


#======================================
# ERROR CHECK FUNCTIONS
#======================================
def handle_report_folder():
	error = False

	try:
		os.mkdir('./reports')
		os.mkdir('./reports/Group_Reports')
	except OSError as e:
		pass

	paths = ['./reports/', './reports/Group_Reports/']

	for path in paths:

		files = [f for f in listdir(path) if isfile(join(path, f))]	
		for file in files:
			try:
				os.remove(path+file)
			except OSError as e:
				print(path,file)
				print ("ERROR: CLOSE ALL OPEN PDF REPORTS!")
				error = True
			if error:
				break
		if error:
			break

	return error


def check_dates():
	error = False
	path = "./data/user_exports/"
	dates = get_dates(path)

	if len(dates) == 0:
		print("ERROR: NO USER EXPORTS FOUND IN DATA FOLDER")
		error = True

	return error


#======================================
# MAIN FUNCTION
#======================================
def main():
	error = handle_report_folder()
	if not error:

		error = check_dates()
		if not error:

			curr_directory, prev_directory = fetch_directories()

			curr_sum_dict, curr_group_dict = fetch_dicts(curr_directory)
			prev_sum_dict, prev_group_dict = fetch_dicts(prev_directory)

			diff_sum_dict, diff_group_dict = fetch_diff_dicts(curr_group_dict, curr_sum_dict, prev_group_dict, prev_sum_dict)

			generate_group_pdf(curr_directory, prev_directory, curr_group_dict, diff_group_dict)
			generate_sum_pdf(curr_directory, prev_directory, curr_sum_dict, diff_sum_dict)


main()