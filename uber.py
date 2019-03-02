import pandas as pd
import seaborn as sns
import matplotlib as mp
import numpy as np

def t_o_d(x):
	if x == 23 or x < 3:
		return('midnight')
	elif 3 <= x < 6:
		return('early morning')
	elif 6 <= x < 11:
		return('morning')
	elif 11 <= x < 15:
		return('afternoon')
	elif 15 <= x < 20:
		return('evening')
	elif 20 <= x < 23:
		return('night')

def success(x):
	if x == "Trip Completed":
		return("Success")
	else:
		return("Unsuccessful")


uber_df = pd.read_csv('Uber Request Data.csv')
print(uber_df.info())

#extracting time of request from timestamp for analysis
uber_df['Request timestamp'] = uber_df['Request timestamp'].str[:16]
uber_df['r_time'] = uber_df['Request timestamp'].str[-5:]
uber_df['r_date'] = uber_df['Request timestamp'].str[:10]

#extracting time of day of request
uber_df['r_hour'] = uber_df['r_time'].str.split(':').str[0]
uber_df['r_min'] = uber_df['r_time'].str.split(':').str[1]
uber_df['r_hour'] = pd.to_numeric(uber_df['r_hour'])
uber_df['r_min'] = pd.to_numeric(uber_df['r_min'])
uber_df['time_of_day'] = uber_df['r_hour'].apply(lambda x: t_o_d(x))

#extracting time of completion
uber_df['Drop timestamp'] = uber_df['Drop timestamp'].str[:16]
uber_df['c_time'] = uber_df['Drop timestamp'].str[-5:]
uber_df['c_date'] = uber_df['Drop timestamp'].str[:10]
uber_df['c_hour'] = uber_df['c_time'].str.split(':').str[0]
uber_df['c_min'] = uber_df['c_time'].str.split(':').str[1]
uber_df['c_hour'] = pd.to_numeric(uber_df['c_hour'])
uber_df['c_min'] = pd.to_numeric(uber_df['c_min'])

#sorting the dataframe in sequence
uber_df = uber_df.sort_values(by=['Driver id','r_date','r_hour','r_min'],ascending=True)

#adding metric for successful request
uber_df['Success'] = uber_df['Status'].apply(lambda x : success(x))

#creating new dataframe for successfull trips
uber_success = uber_df[uber_df['Status'] == 'Trip Completed']
uber_success['Drop&Time'] = uber_success['Pickup point'].astype(str).str.cat(uber_success['c_hour'].astype(str), sep='-')
uber_success['Pick&Time'] = uber_success['Pickup point'].astype(str).str.cat(uber_success['r_hour'].astype(str), sep='-')

#doing a groupby operation to monitor time-varying market health
uber_success['airport_inflow'] = uber_success['Drop&Time'].map(uber_success.groupby(['Drop&Time'])['Request id'].count())
uber_success['airport_outflow'] = uber_success['Pick&Time'].map(uber_success.groupby(['Pick&Time'])['Request id'].count())
uber_success.to_csv('uber_success.csv')


#converting time to common unit of minutes to measure idle time
uber_df['r_mins'] = (uber_df['r_hour'] * 60 ) + uber_df['r_min']
uber_df['c_mins'] = (uber_df['c_hour'] * 60 ) + uber_df['c_min']


#creating new dataframes for cancelled and no cars
uber_nocars = uber_df
uber_cancelled = uber_df
uber_nocars = uber_df[uber_df.Status == 'No Cars Available']
uber_cancelled = uber_df[uber_df.Status == 'Cancelled']


#visualizing general volume of requests
sns.catplot(x="Pickup point", kind="count", data=uber_df)
mp.pyplot.show()
mp.pyplot.close()


#visualizing general volume of requests
sns.catplot(x="Pickup point", kind="count", hue='time_of_day', data=uber_df)
mp.pyplot.show()
mp.pyplot.close()

#visualizing market health based on time-of-day
sns.catplot(x="time_of_day", hue="Success", col='Pickup point', kind="count", data=uber_df)
mp.pyplot.show()
mp.pyplot.close()


#visualizing supply and demand
sns.catplot(x='r_hour',data = uber_df, hue='Pickup point', col = 'Status', kind='count')
sns.catplot(x='r_hour',data = uber_df, hue='Pickup point', col = 'Success', kind='count')
sns.catplot(x='r_hour',data = uber_df, col = 'Pickup point', kind='count')
sns.catplot(x="Status", y="r_hour", hue="Pickup point", kind="violin", data=uber_df[uber_df['Success']=='Unsuccessful'])
mp.pyplot.show()
mp.pyplot.close()

#visualizing hourly inflow at airports and cities
#sns.lineplot(x="c_hour", y='airport_inflow', data=uber_success[uber_success['Pickup point']=='City'], legend='full', hue='Pickup point')
#mp.pyplot.show()
#sns.lineplot(x="r_hour", y='airport_outflow', data=uber_success[uber_success['Pickup point']=='Airport'], legend='full', hue='Pickup point')
#mp.pyplot.show()
#mp.pyplot.close()
x1 = np.array(uber_success[uber_success['Pickup point']=='City']['c_hour'])
y1 = np.array(uber_success[uber_success['Pickup point']=='City']['airport_inflow'])

x2 = np.array(uber_success[uber_success['Pickup point']=='Airport']['r_hour'])
y2 = np.array(uber_success[uber_success['Pickup point']=='Airport']['airport_outflow'])

mp.pyplot.plot(x1,y1,'ro')
mp.pyplot.plot(x2,y2,'bo')

mp.pyplot.show()
mp.pyplot.close()

sns.catplot(x="Pickup point", y="airport_outflow", hue="time_of_day", kind="box", data=uber_success[uber_success['Pickup point']=='City'])
sns.catplot(x="Pickup point", y="airport_inflow", hue="time_of_day", kind="box", data=uber_success[uber_success['Pickup point']=='Airport'])
mp.pyplot.show()
mp.pyplot.close()

