
import requests
import json
from datetime import datetime
from datetime import timedelta
import pandas as pd
import os,sys
import logging

def Fetch_Pullrequest_Summary(username, reponame):
		now = datetime.now().strftime('%Y-%m-%d')
		date_lastweek = datetime.now() - timedelta(days=60)

		lastweek = date_lastweek.strftime('%Y-%m-%d')
		root_url = "https://api.github.com/repos/%s/%s/pulls1?state=all" % (username,reponame)

		headers = {
			"Content-Type":"application/json",
			"X-Requested-With": "XMLHttpRequest"
		}

		details = []
		closed = 0
		opened = 0
		draft = 0
		merged = 0
		page = 1
		TotalPullRequest = 0
		page = 1
		cont_flag = True

		while(cont_flag) :
			try :
				url = root_url + ("&page=%s&per_page=100" % page)
				logging.info("Calling url - %s", url)

				resp = requests.request('GET', url, headers=headers)
				if(resp.status_code == 200):
					resp1= json.loads(resp.text)
					
					## Default page output is 30, which can be increased to 100
					if len(resp1) >= 30:
						cont_flag = True
						page += 1
					else:
						cont_flag = False
					
					for Pull_req in resp1:
						created_at = datetime.strptime(Pull_req["created_at"], '%Y-%m-%dT%H:%M:%SZ')
						if date_lastweek >= created_at:
							break

						TotalPullRequest += 1
						
						state = Pull_req["state"]

						if Pull_req["draft"] == 'true':
							draft += 1
							state = "draft"
						elif Pull_req["merged_at"] != None:
							merged += 1
							state = "merged"
						elif Pull_req["state"] == 'open':
							opened += 1
							state = "open"
						elif Pull_req["state"] == 'closed':
							closed += 1
							state = "closed"

						obj = {}
						obj["Pull Request Number"] = Pull_req["number"]
						obj["State"] = state
						obj["Title"] = Pull_req["title"]
						obj["Created_at"] = Pull_req["created_at"]
						obj["Updated_at"] = Pull_req["updated_at"]
						obj["Closed_at"] = Pull_req["closed_at"]
						obj["Merged_at"] = Pull_req["merged_at"]
						obj["Created by"] = Pull_req["user"]["login"]
						obj["Base <- Head"] = Pull_req["base"]["label"] + " <- " + Pull_req["head"]["label"]
						obj["Assignees"] = ','.join([asignee["login"] for asignee in Pull_req["assignees"]])
						obj["Comment"] = Pull_req["body"]
						obj["Commits url"] = Pull_req["commits_url"]
						

						details.append(obj)
				else:
					logging.info("Error fetching request details. Status code - %s", resp.status_code)
					cont_flag = False
					logging.info("---- Terminating Script ----")
					sys.exit(1)
			
			except Exception as e:
				logging.info("Error while fetching details - %s", e)
				logging.info("---- Terminating Script ----")
				sys.exit(1)
		
		
		details_page = "https://github.com/%s/%s/pulls?" % (username,reponame)
		details_page = details_page +"q=is%3Apr+state%3Aall+created%3A%3E%3D" + lastweek
		
		df = pd.DataFrame(details)
		output_file = output_folder + "Output.xlsx"
		
		logging.info("Writing to Attachment file - %s", output_file)
		df.to_excel(output_file,index=False)
		
		Email_Body = """
		From : Automation@testemail.com
		To : Test@testemail.com
		Subject : Pull Request Summary | %s
		Attachment : %s
		Body :
			Hi Team, <br>
			<br>
			Please find below summary for Pull Requets for last week (%s - %s) :<br>
			<br>
			Repo : %s/%s <br>
			Total Pull Requests : %s <br>
			Opened Pull Requests : %s <br>
			Closed Pull Requests : %s <br>
			Draft Pull Requests : %s <br>
			Merged Pull Requests : %s <br>
			<br>
			<br>
			Find Attached 'Pull Request' Report with this mail.<br>
			For more details, visit this link - %s
			<br>
			<br>
			Regards,
			DevOps Team
		""" % (now, output_file, now, lastweek, username, reponame, TotalPullRequest, opened, closed, draft, merged, details_page)

		print(Email_Body)	

if __name__ == '__main__': 
	ScriptPath = os.path.dirname(os.path.abspath(__file__))
	
	if '/' in ScriptPath:
		PathSlash = '/'
	else:
		PathSlash = '\\'
	

	path_arr = ScriptPath.split(PathSlash)
	path_arr.pop()
	parent_path = (PathSlash).join(path_arr)
	

	log_folder = parent_path + PathSlash + 'logs' + PathSlash
	output_folder = parent_path + PathSlash + 'output' + PathSlash

	if not os.path.exists(log_folder):
		os.makedirs(log_folder)
	if not os.path.exists(output_folder):
		os.makedirs(output_folder)
	
	log_file = log_folder + 'Log_' + datetime.now().strftime("%Y-%m-%d") + '.log'
	logging.basicConfig(filename=log_file,format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',level=logging.INFO)
	#logging.basicConfig(filename=log_file, format='%s(asctime)s - %(message)s', level=logging.INFO)
	logging.info("---- Starting Script ----")
	username='JeetenderK'
	reponame='TomcatSample'

	username='AppFlowy-IO'
	reponame='AppFlowy'

	Fetch_Pullrequest_Summary(username, reponame)
	logging.info("---- Ending Script ----")
	sys.exit(0)