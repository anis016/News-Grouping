DATABASE_NAME = "businessData"
MONGO_URI = "mongodb://localhost:27017/"

# trick to resolve import issue:
# use sys.path to see till what path python sees, then use the path after that.
# import sys
# print("Project Path:: " + str(sys.path))

######################################################
# load the configurations
import common.utils as utils
payload = utils.load_configurations(config_file_name='bdm_configurations.json')

COLLECTION_LISTENER  = payload["listener_collections"]
COLLECTION_PROCESSING= payload["processing_collections"]
COLLECTION_STOCK     = payload["matching_collections"][0].get("stockCollection")
SIMILARITY_ALGORITHM = payload["keyword_algorithm"]
SIMILARITY_MEASURES  = payload["similarity_measure"]
SIMILARITY_THRESHOLD = payload["similarity_threshold"]
######################################################

## Test Datasets
data_set1 = '''
 Transaction-could be announced at Farnborough Airshow in July

Volga-Dnepr in talks for at least 10 Boeing 747-8 freighters

Boeing Co. is nearing a $4 billion deal with Russia’s largest air-freight company that would help extend the life of the iconic, hump-nosed 747 jumbo jet amid waning demand for four-engine aircraft, people close to the transaction said.
'''

data_set2 = '''
 WAUKEGAN, Ill. (AP) - The Waukegan School Board has approved a New Jersey company's $3 million donation of solar panels for seven school buildings.

The (Lake County) News-Sun reports (http://trib.in/28J5Mn7 ) the project with NRG was delayed a year because of school officials’ concerns about the district’s liability if something happened to the equipment. A subcontractor will be required to meet standards the board demands.

NRG spokesman David Gaier says the company plans to complete installation by the end of August with energy delivery beginning by year’s end.

Gaier says each solar station will produce its own statistics about energy production, temperature, wind speed and more. NRG also supplies an energy-related curriculum for use in the classroom.

School board vice president Rick Riddle is pleased with the educational opportunity provided.

___

Information from: Lake County News-Sun, http://newssun.chicagotribune.com/
'''

# This is the Test dataSet for the possible match/non-match
data_set3 = '''
hello
hello-world
company's
asd890
--- ?? +++ (AL)
http://something
'''


data_set4= '''
'WASHINGTON, June 20, 2016 /PRNewswire-USNewswire/ -- SHRM: 20-Year Employee Benefits Trends in the United States -- Now and Then. Telecommuting, bonuses...'
'''

news_source = [
"http://www.prnewswire.com/news-releases/shrm-20-year-employee-benefits-trends-in-the-united-states--now-and-then-300286640.html",
"http://www.spacedaily.com/reports/NASA_Electric_Research_Plane_Gets_X_Number_New_Name_999.html",
"http://www.bloomberg.com/news/articles/2016-06-20/boeing-said-near-4-billion-deal-with-russian-firm-to-save-747",
"https://www.bostonglobe.com/business/2016/06/20/india-makes-easier-for-foreign-firms-invest-many-industries/GIzrXlcVBwFtPvCVwNknNM/story.html",
"http://www.marketwatch.com/story/djia-points-to-200-point-gain-as-polls-show-brexit-support-weakening-2016-06-20"
# "http://www.washingtontimes.com/news/2016/jun/20/company-to-donate-solar-energy-systems-to-7-waukeg"
]