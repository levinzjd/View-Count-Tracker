#Import packages used in this tracker
import time
import requests
import threading

class get_ct():
    def __init__(self,user,subdomain,api_token,ids,on=True):
        self.user = user + '/token'
        self.subdomain = subdomain
        self.pwd = api_token
        self.ids = ids        
        self.on = on
	
	#Fucntin to get the ticket counts for the view id entered
    def get_view_count(self):
		#The output files are suffixed with the output time
        now = str(time.strftime('%Y%m%d_%H_%M_%S', time.localtime(time.time())))

        #Get view list
        url1 = 'https://{}.zendesk.com/api/v2/views.json'.format(self.subdomain)
        response = requests.get(url1, auth=(self.user, self.pwd))
        obj =response.json()

        #Map view ids and view titles
        id_dict = {}
        for view in obj['views']:
            if view['id'] in [int(x) for x in ids.split(',')]:
                id_dict[view['id']] = view['title']

        #Get view counts    
        payload={'ids':self.ids}
        url2 = 'https://{}.zendesk.com/api/v2/views/count_many.json'.format(self.subdomain)
        response2 = requests.get(url2, auth=(self.user, self.pwd),params=payload)
        obj2 =response2.json()

        #Map view ids and view counts
        ct_dict={}
        for view in obj2['view_counts']:
            ct_dict[view['view_id']] = view['value']

        #Merge view id, view title and view count
        ds = [id_dict, ct_dict]
        d = {}
        for k in id_dict.keys():
            d[k] = tuple(d[k] for d in ds)
		
		#Write out the view id, view title and view count to csv
        with open('ViewCounts_{0}.csv'.format(now) , 'w') as f:
            f.write('view_ids,view_titles,ticket_counts\n')
            for key, value in d.items():
                f.write('{0},{1},{2}\n'.format(key, value[0], value[1]))
		
		#print out the time when exporting a csv file
        print (now)
	
	#Function to run the get_view_count every 10 mins
    def run(self):
        if self.on:
            threading.Timer(600.0,  self.run).start() # call this function every 10 minute (600 seconds)
            self.get_view_count()
        else:
            print('Turned off tracker')

#Enter the information for user and the view ids need to tracked
user = input('email: ')
subdomain = input('subdomain: ')
api_token = input('api token: ')
ids = input('view ids: ')

#Create a object based on the information entered
tracker = get_ct(user,subdomain,api_token,ids)
#Start to track
tracker.run()