## -*- coding: utf-8 -*-
##  SortTweets.py
##

__author__ = "Peter Hauck"
__email__ = "phauck@vt.edu"

import json
import os
import math
import sys
import time


def distance_on_unit_sphere(lat1, long1, lat2, long2):
    # Convert latitude and longitude to 
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0
    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
    # Compute spherical distance from spherical coordinates.
    # For two locations in spherical coordinates 
    # (1, theta, phi) and (1, theta', phi')
    # cosine( arc length ) = 
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )*3959#earth's radius is 3959 miles
    return arc


def dist_from_mizzou(tweet_lat, tweet_long):
    mizzou_lat = 38.9453
    mizzou_long = -92.3288
    return distance_on_unit_sphere(mizzou_lat, mizzou_long, tweet_lat, tweet_long)

def dist_from_newhaven(tweet_lat, tweet_long):
    newhaven_lat = 41.31
    newhaven_long = -72.923611
    return distance_on_unit_sphere(newhaven_lat, newhaven_long, tweet_lat, tweet_long)

def dist_from_princeton(tweet_lat, tweet_long):
    princeton_lat = 40.357115
    princeton_long = -74.670165
    return distance_on_unit_sphere(princeton_lat, princeton_long, tweet_lat, tweet_long)

def dist_from_oxmiss(tweet_lat, tweet_long):
    oxmiss_lat = 34.359722
    oxmiss_long = -89.526111
    return distance_on_unit_sphere(oxmiss_lat, oxmiss_long, tweet_lat, tweet_long)

def dist_from_blacksburg(tweet_lat, tweet_long):
    blacksburg_lat = 37.23
    blacksburg_long = -80.417778
    return distance_on_unit_sphere(blacksburg_lat, blacksburg_long, tweet_lat, tweet_long)

def dist_from_statecollege(tweet_lat, tweet_long):
    statecollege_lat = 40.791389
    statecollege_long = -77.858611
    return distance_on_unit_sphere(statecollege_lat, statecollege_long, tweet_lat, tweet_long)


def locateByName(e,name):
    if e.get('name',None) == name:
        return e

    for child in e.get('children',[]):
        result = locateByName(child,name)
        if result is not None:
            return result

    return None

def HasLocData(json_tweet):
    loc = locateByName(json_tweet,location)
    if loc is not None:
       return True

def is_json(myjson):
  try:
    json_object = json.loads(myjson)
  except ValueError, e:
    return False
  return True



def main():

    fname = sys.argv[1]

    str_fname_us_en = fname+'_us_eng'
    file_us_en = open(str_fname_us_en, 'w+')

    str_fname_mizzou = fname+'_mizzou'
    file_mizzou =  open(str_fname_mizzou, 'w+')

    str_fname_newhaven = fname+'_newhaven'
    file_newhaven =  open(str_fname_newhaven, 'w+')

    str_fname_princeton =  fname+'_princeton'
    file_princeton =  open(str_fname_princeton, 'w+')

    str_fname_oxmiss= fname+'_oxmiss'
    file_oxmiss =  open(str_fname_oxmiss, 'w+')

    str_fname_oxmiss = fname+'_blacksburg'
    file_blacksburg =  open(str_fname_oxmiss, 'w+')

    str_fname_statecollege = fname+"_statecollege"
    file_statecollege =  open(str_fname_statecollege, 'w+')

    with open(fname) as f:
         for line in f:
       
             if is_json(line):
                j_content = json.loads(line)

                if 'profileLocations' in j_content['gnip']:
                    country = j_content['gnip']['profileLocations'][0]['address']['country']
                    if country == "United States":
                       lang = j_content['twitter_lang']
                       if lang == 'en':
                          file_us_en.write(line)    
                          tweet_nominal_locality = 'None'
                          if 'locality' in j_content['gnip']['profileLocations'][0]['address']:
                              tweet_nominal_locality = j_content['gnip']['profileLocations'][0]['address']['locality']                         
                              tweet_long =  j_content['gnip']['profileLocations'][0]['geo']['coordinates'][0]
                              tweet_lat = j_content['gnip']['profileLocations'][0]['geo']['coordinates'][1]
                                             
                             if dist_from_mizzou(tweet_lat, tweet_long) < 2 or tweet_nominal_locality == 'Columbia':
                                file_mizzou.write(line)
                             if dist_from_newhaven(tweet_lat, tweet_long) < 2 or  tweet_nominal_locality == 'New Haven':
                                file_newhaven.write(line)
                             if dist_from_princeton(tweet_lat, tweet_long) < 2 or tweet_nominal_locality == 'Princeton':
                                file_princeton.write(line)
                             if dist_from_oxmiss(tweet_lat, tweet_long) < 2 or tweet_nominal_locality == 'Oxford':
                                file_oxmiss.write(line)
                             if dist_from_blacksburg(tweet_lat, tweet_long) < 2 or tweet_nominal_locality == 'Blacksburg':
                                file_blacksburg.write(line)
                             if dist_from_statecollege(tweet_lat, tweet_long) < 2 or tweet_nominal_locality == 'State College':
                                file_statecollege.write(line)       

if __name__ == '__main__':
    main()

