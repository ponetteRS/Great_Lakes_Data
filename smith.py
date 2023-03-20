#imports
import requests as re
import json
import os
import sqlite3
import pandas as pd


#read glansis tracking into csv, has species list to query
#automation step: file editable to client
tracking = pd.read_csv("/Users/madelinetrumbauer/Local Desktop/F '21/SI 485/Tracking.csv")

#store Scientific Name in tracking as list called species
#species = tracking['Scientific Name'].to_list()
#print(species) 

#read glansis bulk upload template
bulk = pd.read_csv("/Users/madelinetrumbauer/Local Desktop/F '21/SI 485/bulk.csv")
#print(bulk)

#create dataframe to store smithsonian data 
smithsonian_df= pd.concat([bulk, tracking['Scientific Name']])
#print(smithsonian_df)
#print(smithsonian_df)

#change index col, species, to the name species
smithsonian_df.rename(columns={0:"species"}, inplace = True)

#drop first row of text descriptions of each column
smithsonian_df = smithsonian_df.tail(-1)
#print(smithsonian_df)


#narrows output table df to only mandatory columns
#smithsonian_table = smithsonian_df
#smithsonian_table= smithsonian_df[['species', 'Genus*', 'Species*', 'Latitude*', 'Source*', 'Accuracy*', 'Locality*']]
#print(smithsonian_table.columns)

#add 'scientific name' as column
#smithsonian_table['scientific_name'] = ""

#searches for a species with the Smithsonian 'search' API returns the text of the whole query result
def make_a_query(key,query):
    base_url = 'https://api.si.edu/openaccess/api/v1.0/search'
    params_dict={'api_key':key, 'q':query}
    first_search = re.get(base_url, params_dict)
    first_result = json.loads(first_search.text)
    return first_result

#to get the scientific name of a speices
def title(result):
    dict_of_titles = {}
    for i in range(len(result['response']['rows'])):
        title= result['response']['rows'][i]['content']['descriptiveNonRepeating']['title']['content']
        title_string=json.dumps(title)
        dict_of_titles[i] = title_string
         #add each name to scientific_name in df
    #titles_series= pd.Series(list_of_titles)
    #smithsonian_df['scientific_name'].append(titles_series)
    #print(smithsonian_df)
    #for i in titles_series:
        #output_table['scientific_name'].append(i)
    #print(list_of_titles)
        #output_table.at(1, 'scientific_name') 
    return dict_of_titles

def scientific_name(result):
    dict_of_sci_name = {}
    for i in range(len(result['response']['rows'])):
        sci_name = result['response']['rows'][i]['content']['indexedStructured']['scientific_name'][0]
        sci_name_string=json.dumps(sci_name)
        dict_of_sci_name[i] = sci_name_string
    return dict_of_sci_name

#break up scientific name and store as Genus and Species


#get latitude and longitude of species
#def latlong(first_result):




#get locality  description and store in dictionary
def locality(first_result):
    locality_dict = {}
    for i in range(len(first_result['response']['rows'])):
        if "name" in first_result['response']['rows'][i]['content']['freetext'] and "place" in first_result['response']['rows'][i]['content']['freetext'] and 'geoLocation' in first_result['response']['rows'][i]['content']['indexedStructured']:
            name = first_result['response']['rows'][i]['content']['freetext']['name'][0]['content']
            place = first_result['response']['rows'][i]['content']['freetext']['place'][0]['content']
            if 'Other' in first_result['response']['rows'][i]['content']['indexedStructured']['geoLocation'][0]:
                    other = first_result['response']['rows'][i]['content']['indexedStructured']['geoLocation'][0]['Other']['content']
                    locality_dict[i] = name, place, other 
            else:
                locality_dict[i] = name, place
        elif "name" in first_result['response']['rows'][i]['content']['freetext'] and "place" in first_result['response']['rows'][i]['content']['freetext'] and 'geoLocation' not in first_result['response']['rows'][i]['content']['indexedStructured']:
                name = first_result['response']['rows'][i]['content']['freetext']['name'][0]['content']
                place = first_result['response']['rows'][i]['content']['freetext']['place'][0]['content']
                locality_dict[i] = name, place
        elif "name" in first_result['response']['rows'][i]['content']['freetext'] and "place" not in first_result['response']['rows'][i]['content']['freetext'] and 'geoLocation' in first_result['response']['rows'][i]['content']['indexedStructured']:
                name = first_result['response']['rows'][i]['content']['freetext']['name'][0]['content']
                if 'Other' in first_result['response']['rows'][i]['content']['indexedStructured']['geoLocation'][0]:
                    other = first_result['response']['rows'][i]['content']['indexedStructured']['geoLocation'][0]['Other']['content']
                    locality_dict[i] = name, other 
                else:
                     locality_dict[i] = name
        elif "name" not in first_result['response']['rows'][i]['content']['freetext'] and "place" in first_result['response']['rows'][i]['content']['freetext'] and 'geoLocation' in first_result['response']['rows'][i]['content']['indexedStructured']:
                place = first_result['response']['rows'][i]['content']['freetext']['place'][0]['content']
                if 'Other' in first_result['response']['rows'][i]['content']['indexedStructured']['geoLocation'][0]:
                    other = first_result['response']['rows'][i]['content']['indexedStructured']['geoLocation'][0]['Other']['content']
                    locality_dict[i] = place, other 
                else:
                     locality_dict[i] = place
        elif "name" in first_result['response']['rows'][i]['content']['freetext']:
            name = first_result['response']['rows'][i]['content']['freetext']['name'][0]['content']
            locality_dict[i] = name
        elif "place" in first_result['response']['rows'][i]['content']['freetext']:
            place = first_result['response']['rows'][i]['content']['freetext']['place'][0]['content']
            locality_dict[i] = place
        elif 'geoLocation' in first_result['response']['rows'][i]['content']['indexedStructured']:
            if 'Other' in first_result['response']['rows'][i]['content']['indexedStructured']['geoLocation'][0]:
                other = first_result['response']['rows'][i]['content']['indexedStructured']['geoLocation'][0]['Other']['content']
                locality_dict[i] = other 
        else:
            locality_dict[i] = float("NaN")
            #float("NaN"); used to be
        # locality_list.append(locality)
    return locality_dict

def location(first_result):
    location_dict = {}
    for i in range(len(first_result['response']['rows'])):
        if'geoLocation' in first_result['response']['rows'][i]['content']['indexedStructured']:
            if 'L4' in first_result['response']['rows'][i]['content']['indexedStructured']['geoLocation'][0]:
                county = first_result['response']['rows'][i]['content']['indexedStructured']['geoLocation'][0]['L4']['content']
                county_string = json.dumps(county)
            else:
                 county_string = float("NaN")
            if 'L3' in first_result['response']['rows'][i]['content']['indexedStructured']['geoLocation'][0]:
                state = first_result['response']['rows'][i]['content']['indexedStructured']['geoLocation'][0]['L3']['content']
                state_string = json.dumps(state)
            else:
                 state_string = float("NaN")
            if 'L2' in first_result['response']['rows'][i]['content']['indexedStructured']['geoLocation'][0]:
                country = first_result['response']['rows'][i]['content']['indexedStructured']['geoLocation'][0]['L2']['content']
                country_string = json.dumps(country)
            else:
                 country_string = float("NaN")
            if 'L1' in first_result['response']['rows'][i]['content']['indexedStructured']['geoLocation'][0]:
                continent = first_result['response']['rows'][i]['content']['indexedStructured']['geoLocation'][0]['L1']['content']
                continent_string = json.dumps(continent)
            else:
                 continent_string = float("NaN")
            # location_string = county_string + ", " + state_string + ", " + country_string + ", " + continent_string
            location_dict[i] = county_string, state_string, country_string, continent_string
        else:
            location_dict[i] = float("NaN")
    return location_dict
#potentially zip with locality before inserting into GLANSIS spreadsheet


#categorize source of location, may have to calculate HUC by county

#categorize Accuracy of observation (Accurate)

#get year
def year(first_result):
    year_dict = {}
    for i in range(len(first_result['response']['rows'])):
        if 'date' in first_result['response']['rows'][i]['content']['indexedStructured']:
            year = first_result['response']['rows'][i]['content']['indexedStructured']['date']
            year_dict[i] = year
        else: year_dict[i] = float("NaN")
    return year_dict
     

#categorize year accuracy of specimen


#categorize record type

def main():
    #smithsonian to build df
    intermediary_df = pd.DataFrame(columns = ['species', 'title', 'locality', 'location', 'year'])
    # cool = make_a_query('11icycZDd63MfM3OrfwyQwrpJatRz5mFy37cnBo6',smithsonian_df['species'])
    # #^to test do .iloc[2]
    # species_title = title(cool)
    # species_locality = locality(cool)
    # species_location = location(cool)
    # species_year = year(cool)
    # # # of rows already rows in the intermediary_df + j in square
    # for j in range(len(species_title)):
    #     intermediary_df = intermediary_df.append({'species': species_title[j], 'title':species_title[j], 'locality':species_locality[j], 'location': species_location[j], 'year':species_year[j]}, ignore_index=True)
    # print(intermediary_df)
    # intermediary_df.to_csv('intermediary_df_full.csv')
    # print(species_title)
    #cool = make_a_query('11icycZDd63MfM3OrfwyQwrpJatRz5mFy37cnBo6', smithsonian_df['species'].iloc[10])
    #print(scientific_name(cool))
    #print(cool)
    #print(locality(cool)) #first locality function
    #print(location(cool)) #second locality function
    #print(year(cool))
    # for i in smithsonian_df['species']:
    #     cool = make_a_query('11icycZDd63MfM3OrfwyQwrpJatRz5mFy37cnBo6', i) #saved as a json object. it is the file
    #     get_scientific_name(cool)
    # smithsonian_df

    #build intermediary dataframe
    #i, scientific name, locality, location, year
    #GOOOOOOOD
    # intermediary_df = pd.DataFrame(columns = ['species', 'title', 'locality', 'location', 'year'])
    # # #loop through species
    for i in smithsonian_df['species']:
        cool = make_a_query('11icycZDd63MfM3OrfwyQwrpJatRz5mFy37cnBo6', i)
       
        species_title = title(cool)
        species_locality = locality(cool)
        species_location = location(cool)
        species_year = year(cool)
    # # of rows already rows in the intermediary_df + j in square
        for j in species_title:
            intermediary_df = intermediary_df.append({'species': i, 'title':species_title[j], 'locality':species_locality[j], 'location': species_location[j], 'year':species_year[j]}, ignore_index=True)
        print(intermediary_df.info())
        
    print(intermediary_df.info())
         # IMPORTANT for script
    print(intermediary_df)
    intermediary_df.to_csv('intermediary_df2.csv')
        # US_df = intermediary_df[intermediary_df['locality'].str.contains('United States|Canada')]
        # print(US_df)
        # US_df.to_csv('US_df.csv')

                  
                   
   
        
    
    



    

#main called
if __name__ == "__main__":
    main()  

