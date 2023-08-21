"""

Generate the following:
- Animals
    - Birth and Death dates (with sites)
- Sites
    - And corresponding Locations
- Vehicles
    - Just registrations for now
- Keepers
    - not done yet
- Hauliers
    - not done yet
- Movements (and Batches)
    - Select random site
    - Shortlist moveable animals
    - Take random selection and move into batch
    - Create movement instance and assign vehicle before moving to appropriate site
    - Remove animals from batch

    
TODO:
- stop movements running without any available animals
- revert journeys to become movements DONE
- add keepers DONE
- add reports to movements DONE
- add hauliers
- add journeys
- add legs (same as movement but with different attributes?)
- create a "size" variable for sites. So we can have small farms vs mega farms, high traffic low traffic etc.
    - size should also increase likelihood animals are moved to/from there
"""

import pandas as pd
import random
from datetime import datetime, timedelta

# Creating the final dataframe (empty)
headers = ["animal_id", "sex", "species", "site_id", "site_type", "location_id", "easting", "northing", "date_of_birth", "date_of_death",
           "death_site_id", "reason_for_death", "batch_id", "date_added_to_batch", "date_removed_from_batch", "vehicle_reg", "movement_id",
           "movement_origin", "movement_destination", "movement_start_date", "movement_end_date", "keeper_id", "keeper_name",
           "report_id", "report_date"]
df = pd.DataFrame(columns=headers)

####################
###### CONFIG ######
####################

# How many of each animal?
animal_config = {
    "cow": 40,
    "pig": 75,
    "sheep": 100
}

# How many of each site?
site_config = {
    "farm": 5,
    "market": 2,
    "slaughterhouse": 2
}

# Number of vehicles and movements
number_of_vehicles = 8
number_of_movements = 50


# Dates config
birth_start_date = datetime(2010, 1, 1)  # Start date for births that will increase by 1-3 days randomly
death_start_date = datetime(2011, 1, 1)  # Start date for births that will increase by 1-3 days randomly



#######################
## Animal Generation ##
#######################

animals_df = pd.DataFrame(columns=["animal_id", "sex", "species"])

id = 1  # Starting ID
for animal_species in animal_config.keys():
    for _ in range(animal_config[animal_species]):
        new_row = {"animal_id": f"animal_{id}",
                   "sex": random.choice(["m", "f"]),
                   "species": animal_species}
        id += 1
        
        animals_df = animals_df._append(new_row, ignore_index=True)

# Appending to the main dataframe
df = df._append(animals_df)


################################
### Site & Keeper Generation ###
################################

sites_and_keepers_df = pd.DataFrame(columns=["site_id", "site_type", "location_id", "easting", "northing", "keeper_id", "keeper_name"])

id = 1  # Starting ID
for site_type in site_config.keys():
    for _ in range(site_config[site_type]):
        new_row = {"site_id": f"site_{id}",
                   "site_type": site_type, 
                   "location_id": f"loc_{id}", 
                   "easting": f"44{random.randint(100, 999)}", 
                   "northing": f"20{random.randint(100, 999)}",
                   "keeper_id": f"keeper_{id}",
                   "keeper_name": "John Smith"}
        id += 1
        
        sites_and_keepers_df = sites_and_keepers_df._append(new_row, ignore_index=True)

# Appending to the main dataframe
df = df._append(sites_and_keepers_df)



##########################
### Vehicle Generation ###
##########################

# Hardcoded reg plates for now, there is another file called reg_gen that creates them
vehicles_dict = {"vehicle_reg": ["WB23964", "XW23940", "HL23445", "BG23024", "NP23422",
                                 "HK23967", "EI23649", "VR23403", "VM23859", "OW23921"]}
vehicles_df = pd.DataFrame(data=vehicles_dict)

# Appending to the main dataframe
df = df._append(vehicles_df, ignore_index=True)




########################
### Birth Generation ###
########################

births_df = pd.DataFrame(columns=["date_of_birth", "animal_id", "site_id"])
birth_date = birth_start_date

for animal_id in df["animal_id"][df["animal_id"].notnull()].unique():
    birth_date += timedelta(days=random.randint(1, 3))
    new_row = {"date_of_birth": birth_date,
            "animal_id": animal_id,
            "site_id": random.choice(df.loc[df['site_type'] == 'farm', 'site_id'].tolist())}
        
    births_df = births_df._append(new_row, ignore_index=True)

# Appending to the main dataframe
df = df._append(births_df)




########################
### Death Generation ###
########################

# Generate deaths for 30% of animals
deaths_df = pd.DataFrame(columns=["date_of_death", "reason_for_death", "animal_id", "death_site_id"])
death_date = death_start_date

for animal_id in df["animal_id"][df["animal_id"].notnull()].unique():
    death_date += timedelta(days=random.randint(1, 3))
    if random.randint(1, 10) < 4:
        new_row = {"date_of_death": death_date,
               "reason_for_death": random.choice(["slaughter", "illness"]),
               "animal_id": animal_id,
               "death_site_id": random.choice(df.loc[df['site_type'] == 'slaughterhouse', 'site_id'].tolist())}
            
        deaths_df = deaths_df._append(new_row, ignore_index=True)

# Appending to the main dataframe
df = df._append(deaths_df)






##########################
### Movement Generation ###
##########################

"""
1. Randomly select origin site and destination site
2. Select eligible animals from origin site
3. Put the animals in a batch
4. Create movement instance and assign variables
5. Remove animals from the batch post-movement
"""

# Resetting the index of the main dataframe
df = df.reset_index(drop=True)



### FUNCTIONS ###

# Select origin and destination sites
def select_origin():
    origin_site = random.choice(df["site_id"][df["site_id"].notnull()].unique())
    return origin_site


# Determine which animals are alive
def alive_animals():
    # for each animal determine if still alive
    all_animals = df["animal_id"].unique()
    dead_animals = df.loc[df["date_of_death"].notnull(), "animal_id"].unique()

    # Convert both Series to sets
    all_animals_set = set(all_animals)
    dead_animals_set = set(dead_animals)
    # Calculate the set difference
    alive_animals_set = all_animals_set - dead_animals_set
    # Convert the result set back to a Series
    return pd.Series(list(alive_animals_set)).dropna()


# Of the alive animals, determine which are at the provided site
def animals_at_site(site):
    # Find most recent movement end date
    alive_animals_df = df[df['animal_id'].isin(alive_animals())]

    # Convert 'movement_end_date' to datetime
    alive_animals_df.loc['movement_end_date'] = pd.to_datetime(alive_animals_df['movement_end_date'])

    # Sort DataFrame by 'animal_id' and 'movement_end_date'
    alive_animals_df_sorted = alive_animals_df.sort_values(by=['animal_id', 'movement_end_date'])
    # earliest_start_date = alive_animals_df_sorted['movement_end_date'].max()  TODO fix this?

    # Keep only the latest row for each unique value in 'animal_id'
    animals_latest_site = alive_animals_df_sorted.groupby('animal_id').tail(1)

    # Filter for the site we want
    filtered_animals_site = animals_latest_site[animals_latest_site["site_id"] == site]
    return filtered_animals_site["animal_id"]


# Select a random site of the selected type
def select_destination(chosen_type):
    possible_sites = df[df["site_type"] == chosen_type]
    return random.choice(possible_sites["site_id"].to_list())


# Create a batch for the animals to complete the movement within
def create_batch(batch_id, animals_to_be_moved, movement_start_date):
    batch_df = pd.DataFrame(columns=["batch_id", "animal_id", "date_added_to_batch"])

    for animal_id in animals_to_be_moved:
        new_row = {
            "batch_id": batch_id,
            "animal_id": animal_id,
            "date_added_to_batch": movement_start_date
        }

        batch_df = batch_df._append(new_row, ignore_index=True)
    
    return batch_df


# Create the movement, report it from origin keeper and "move" the animals. Then remove them from the batch and report the movement from recipient keeper
def create_movement_remove_batch(movement_id, origin_site, destination_site, batch_id, animals_to_be_moved, movement_start_date, movement_end_date):
    movement_df = pd.DataFrame(columns=["movement_id", "movement_origin", "movement_destination", "movement_start_date", "movement_end_date",
                                        "vehicle_reg", "batch_id", "keeper_id", "report_id", "report_time"])

    new_row = {
        "movement_id": movement_id,
        "movement_origin": origin_site,
        "movement_destination": destination_site,
        "movement_start_date": movement_start_date,
        "movement_end_date": movement_end_date,
        "vehicle_reg": random.choice(df.loc[df['vehicle_reg'].notnull(), 'vehicle_reg'].tolist()),
        "batch_id": batch_id,
        "keeper_id": f"keeper_{origin_site.split('_')[-1]}",
        "report_id": f"{movement_id}_0",
        "report_date": movement_start_date
    }

    movement_df = movement_df._append(new_row, ignore_index=True)

    # Take animals out of batch
    remove_batch_df = pd.DataFrame(columns=["batch_id", "animal_id", "date_removed_from_batch", "report_id", "report_time"])

    for animal_id in animals_to_be_moved:
        new_row = {
            "batch_id": batch_id,
            "animal_id": animal_id,
            "date_removed_from_batch": movement_end_date
        }

        remove_batch_df = remove_batch_df._append(new_row, ignore_index=True)

    # Report the movement after journey is complete
    arrival_report_df = pd.DataFrame(columns=["movement_id", "keeper_id", "report_id", "report_time"])

    new_row = {
        "movement_id": movement_id,
        "keeper_id": f"keeper_{destination_site.split('_')[-1]}",
        "report_id": f"{movement_id}_1",
        "report_date": movement_end_date
    }

    arrival_report_df = arrival_report_df._append(new_row, ignore_index=True)
    
    return movement_df, remove_batch_df, arrival_report_df



# Each iteration of this code creates 1 movement
movement_start_date = birth_start_date + timedelta(days=500)

for i in range(number_of_movements):

    # Select origin site randomly
    origin_site = select_origin()

    # Shortlist animals eligible for movement
    candidate_animals = animals_at_site(origin_site)

    # while len(candidate_animals) < 1: TODO fix it so we cant do empty movements
    #     origin_site = select_origin()
    #     candidate_animals = animals_at_site(origin_site)

    #     print(origin_site)
    #     print(candidate_animals)
    #     print(len(candidate_animals))

    # Take a selection of the animals available at the site
    animals_to_be_moved = candidate_animals.sample(frac=0.7, random_state=42)

    # Determine destination site based on movement purpose
    destination_types = list(site_config.keys())
    chosen_type = random.choice(destination_types)

    destination_site = select_destination(chosen_type)

    # allow 4-7 days to pass between each movement
    movement_start_date += timedelta(days=random.randint(4, 7))

    # put the chosen animals into a batch and assign start date
    batch_df = create_batch(i, animals_to_be_moved, movement_start_date)
    df = df._append(batch_df)


    # create the movement instance and assign origin, destination, start and end dates, batch, vehicle
    movement_end_date = movement_start_date + timedelta(days=random.randint(1, 3))

    movement_df, remove_batch_df, arrival_report_df = create_movement_remove_batch(i, origin_site, destination_site, i, animals_to_be_moved,
                                                                                    movement_start_date, movement_end_date)
    df = df._append(movement_df)
    df = df._append(remove_batch_df)
    df = df._append(arrival_report_df)

    df = df.reset_index(drop=True)




file_name = "my_dataframe.csv"
df.to_csv(file_name, index=False)
print("dataframe written to csv")
